"""
train.py
========
[역할] 전체 학습 파이프라인을 순서대로 조립하고 실행하는 엔트리포인트.

이 파일 하나만 위에서 아래로 읽으면 Mask R-CNN 학습의 전체 흐름이 보이도록
"조립"만 하고, 실제 구현은 각 모듈에 위임한다.

    config.py     -> 설정값
    dataset.py    -> 데이터 읽기 + target 만들기
    transforms.py -> 증강
    model.py      -> 모델 / 옵티마이저 / 스케줄러
    engine.py     -> 학습 루프 / 평가 루프
    utils.py      -> 시드, 로깅, 체크포인트
    visualize.py  -> 결과 그림 저장

[전체 흐름 9단계]
    1. 설정 로드 & 시드 고정
    2. 데이터셋 생성 (train / val)
    3. DataLoader 생성
    4. (권장) GT 시각화로 데이터 검증
    5. 모델 생성 + 장치로 이동
    6. 옵티마이저 / 스케줄러 생성
    7. epoch 루프: 학습 -> 검증 -> 스케줄러 step -> 체크포인트 저장
    8. 최종 평가 (mAP)
    9. 예측 결과 시각화

실행:
    python make_dummy_dataset.py     # 먼저 샘플 데이터 생성
    python train.py --epochs 5
"""

from __future__ import annotations

import argparse
import json
import os
import time

import torch
from torch.utils.data import DataLoader

from config import Config
from dataset import build_datasets
from engine import evaluate_loss, evaluate_map, train_one_epoch
from model import build_lr_scheduler, build_model, build_optimizer, describe_model
from transforms import build_transforms
from utils import (
    collate_fn,
    count_parameters,
    get_device,
    load_checkpoint,
    save_checkpoint,
    set_seed,
)
from visualize import save_dataset_samples, save_prediction_samples


# ======================================================================
# CLI 인자 파싱 — Config의 기본값을 덮어쓸 수 있게 한다.
# ======================================================================
def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Mask R-CNN 샘플 학습 스크립트")
    parser.add_argument("--data-root", type=str, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--num-workers", type=int, default=None)
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--no-pretrained", action="store_true",
                        help="사전학습 가중치를 쓰지 않음 (오프라인 환경용)")
    parser.add_argument("--amp", action="store_true", help="혼합정밀도 학습 사용 (CUDA 필요)")
    parser.add_argument("--resume", type=str, default=None, help="이어서 학습할 체크포인트 경로")
    args = parser.parse_args()

    cfg = Config()
    # 지정된 인자만 덮어쓴다 (None이면 Config의 기본값 유지).
    if args.data_root is not None:
        cfg.data_root = args.data_root
    if args.epochs is not None:
        cfg.num_epochs = args.epochs
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.lr is not None:
        cfg.lr = args.lr
    if args.num_workers is not None:
        cfg.num_workers = args.num_workers
    if args.output_dir is not None:
        cfg.output_dir = args.output_dir
    if args.no_pretrained:
        cfg.backbone_pretrained = False
    if args.amp:
        cfg.amp = True

    cfg._resume_path = args.resume  # type: ignore[attr-defined]
    return cfg


# ======================================================================
# 메인 파이프라인
# ======================================================================
def main() -> None:
    cfg = parse_args()

    # ------------------------------------------------------------------
    # [단계 1] 설정 출력 / 시드 고정 / 장치 선택
    # ------------------------------------------------------------------
    print("=" * 70)
    print("Mask R-CNN 학습 시작")
    print("=" * 70)
    print(cfg)

    set_seed(cfg.seed)
    device = get_device()
    print(f"\n[장치] {device}")

    os.makedirs(cfg.output_dir, exist_ok=True)
    cfg.save(os.path.join(cfg.output_dir, "config.json"))  # 재현성을 위해 설정 저장

    # AMP는 CUDA에서만 의미가 있다.
    use_amp = cfg.amp and device.type == "cuda"
    scaler = torch.cuda.amp.GradScaler() if use_amp else None
    if cfg.amp and not use_amp:
        print("[경고] CUDA가 없어 AMP를 비활성화합니다.")

    # ------------------------------------------------------------------
    # [단계 2] 데이터셋 생성
    #   학습셋에는 증강을 적용하고, 검증셋에는 적용하지 않는다.
    #   (build_datasets가 그 분리를 처리해 준다 — dataset.py 참고)
    # ------------------------------------------------------------------
    print("\n[단계 2] 데이터셋 준비")
    train_dataset, val_dataset = build_datasets(
        root=cfg.data_root,
        val_ratio=cfg.val_ratio,
        seed=cfg.seed,
        build_transforms_fn=build_transforms,
    )
    print(f"  학습 샘플: {len(train_dataset)}개")
    print(f"  검증 샘플: {len(val_dataset)}개")

    # ------------------------------------------------------------------
    # [단계 3] DataLoader 생성
    #   collate_fn을 반드시 지정해야 한다. (utils.collate_fn의 주석 참고)
    # ------------------------------------------------------------------
    print("\n[단계 3] DataLoader 준비")
    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.batch_size,
        shuffle=True,              # 학습 시에는 매 epoch 순서를 섞는다
        num_workers=cfg.num_workers,
        collate_fn=collate_fn,     # 크기가 제각각인 샘플을 튜플로 묶기
        pin_memory=(device.type == "cuda"),  # GPU 전송 속도 향상
        drop_last=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=1,              # 평가는 배치 1로 하는 편이 결과 매칭이 단순하다
        shuffle=False,             # 평가는 순서를 고정해야 결과를 비교할 수 있다
        num_workers=cfg.num_workers,
        collate_fn=collate_fn,
    )
    print(f"  학습 배치 수: {len(train_loader)} / 검증 배치 수: {len(val_loader)}")

    # ------------------------------------------------------------------
    # [단계 4] 데이터 검증 (매우 권장)
    #   학습을 돌리기 전에 GT가 제대로 만들어졌는지 눈으로 확인한다.
    #   여기서 박스가 엉뚱한 곳에 있으면 학습은 절대 성공하지 않는다.
    # ------------------------------------------------------------------
    print("\n[단계 4] GT 시각화로 데이터 검증")
    save_dataset_samples(
        train_dataset,
        out_dir=os.path.join(cfg.output_dir, "gt_samples"),
        class_names=cfg.class_names,
        num_samples=4,
    )

    # ------------------------------------------------------------------
    # [단계 5] 모델 생성
    # ------------------------------------------------------------------
    print("\n[단계 5] 모델 생성")
    model = build_model(
        num_classes=cfg.num_classes,
        pretrained=cfg.backbone_pretrained,
        trainable_backbone_layers=cfg.trainable_backbone_layers,
        hidden_layer_mask_head=cfg.hidden_layer_mask_head,
    )
    model.to(device)   # 모델을 먼저 장치로 옮긴 뒤 옵티마이저를 만들어야 한다

    print(describe_model(model))
    total_params, trainable_params = count_parameters(model)
    print(f"  전체 파라미터   : {total_params:,}")
    print(f"  학습 파라미터   : {trainable_params:,} "
          f"({100 * trainable_params / total_params:.1f}%)")

    # ------------------------------------------------------------------
    # [단계 6] 옵티마이저 / 스케줄러
    # ------------------------------------------------------------------
    print("\n[단계 6] 옵티마이저 / 스케줄러 생성")
    optimizer = build_optimizer(
        model,
        name=cfg.optimizer,
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay,
    )
    lr_scheduler = build_lr_scheduler(
        optimizer,
        name=cfg.lr_scheduler,
        step_size=cfg.lr_step_size,
        gamma=cfg.lr_gamma,
        num_epochs=cfg.num_epochs,
    )
    print(f"  optimizer: {type(optimizer).__name__} (lr={cfg.lr})")
    print(f"  scheduler: {type(lr_scheduler).__name__ if lr_scheduler else 'None'}")

    # 이어서 학습하기 (--resume)
    start_epoch = 0
    resume_path = getattr(cfg, "_resume_path", None)
    if resume_path:
        start_epoch = load_checkpoint(resume_path, model, optimizer, lr_scheduler, device)

    # ------------------------------------------------------------------
    # [단계 7] 학습 루프
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[단계 7] 학습 루프 시작")
    print("=" * 70)

    history = []               # epoch별 지표 기록 (나중에 그래프로 그릴 수 있음)
    best_val_loss = float("inf")
    training_start = time.time()

    for epoch in range(start_epoch, cfg.num_epochs):
        epoch_start = time.time()

        # --- 7-1. 한 epoch 학습 ---
        train_metrics = train_one_epoch(
            model=model,
            optimizer=optimizer,
            data_loader=train_loader,
            device=device,
            epoch=epoch,
            print_freq=cfg.print_freq,
            warmup_iters=cfg.warmup_iters,
            clip_grad_norm=cfg.clip_grad_norm,
            scaler=scaler,
        )

        # --- 7-2. 학습률 스케줄러 갱신 (epoch 단위) ---
        if lr_scheduler is not None:
            lr_scheduler.step()

        # --- 7-3. 검증 손실 계산 ---
        val_metrics = evaluate_loss(model, val_loader, device, print_freq=cfg.print_freq)

        epoch_time = time.time() - epoch_start
        record = {
            "epoch": epoch,
            "time_sec": round(epoch_time, 1),
            "train": {k: round(v, 4) for k, v in train_metrics.items()},
            "val": {k: round(v, 4) for k, v in val_metrics.items()},
        }
        history.append(record)

        print(f"\n--- Epoch {epoch} 요약 ({epoch_time:.1f}초) ---")
        print(f"  train loss = {train_metrics.get('loss', 0):.4f}")
        print(f"  val   loss = {val_metrics.get('loss', 0):.4f}")
        print("  세부 손실:")
        for key in ("loss_classifier", "loss_box_reg", "loss_mask",
                    "loss_objectness", "loss_rpn_box_reg"):
            if key in train_metrics:
                print(f"    {key:20s}: train {train_metrics[key]:.4f} | "
                      f"val {val_metrics.get(key, 0):.4f}")

        # --- 7-4. 체크포인트 저장 ---
        if (epoch + 1) % cfg.save_every == 0:
            save_checkpoint(
                os.path.join(cfg.output_dir, f"checkpoint_epoch{epoch:03d}.pth"),
                model, optimizer, lr_scheduler, epoch, extra={"config": cfg.to_dict()},
            )

        # 검증 손실이 가장 좋았던 모델을 따로 보관한다 (early stopping의 기본 개념).
        current_val = val_metrics.get("loss", float("inf"))
        if current_val < best_val_loss:
            best_val_loss = current_val
            save_checkpoint(
                os.path.join(cfg.output_dir, "best_model.pth"),
                model, optimizer, lr_scheduler, epoch,
                extra={"config": cfg.to_dict(), "val_loss": current_val},
            )
            print(f"  >> 최고 성능 갱신 (val loss {current_val:.4f})")

    total_time = time.time() - training_start
    print(f"\n[학습 완료] 총 {total_time / 60:.1f}분 소요")

    # 학습 기록을 JSON으로 남긴다.
    with open(os.path.join(cfg.output_dir, "history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # [단계 8] 최종 성능 평가 (mAP)
    #   loss는 "학습이 진행되고 있는가"를 보여 줄 뿐,
    #   실제 검출 성능은 mAP 같은 지표로 측정해야 한다.
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("[단계 8] 최종 평가 (mAP)")
    print("=" * 70)
    metrics = evaluate_map(model, val_loader, device, iou_threshold=0.5)
    for name, value in metrics.items():
        print(f"  {name:24s}: {value:.4f}")

    # ------------------------------------------------------------------
    # [단계 9] 예측 결과 시각화
    # ------------------------------------------------------------------
    print("\n[단계 9] 예측 결과 시각화")
    save_prediction_samples(
        model=model,
        dataset=val_dataset,
        device=device,
        out_dir=os.path.join(cfg.output_dir, "predictions"),
        class_names=cfg.class_names,
        score_threshold=cfg.score_threshold,
        num_samples=4,
    )

    print(f"\n모든 결과가 '{cfg.output_dir}' 에 저장되었습니다.")


if __name__ == "__main__":
    # Windows에서 num_workers > 0 을 쓰려면 이 가드가 반드시 필요하다.
    # (자식 프로세스가 이 모듈을 다시 import 하면서 무한 재귀가 발생하기 때문)
    main()
