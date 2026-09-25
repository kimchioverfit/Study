"""
engine.py
=========
[역할] 실제 "학습 한 epoch"과 "평가 한 epoch"을 수행하는 루프.

[Mask R-CNN 학습 루프의 가장 헷갈리는 점 — 반드시 이해할 것]

    torchvision의 detection 모델은 **모드에 따라 반환값이 완전히 다르다.**

    model.train() 상태에서 model(images, targets) 호출
        -> loss들의 dict 를 반환한다.  (예측 결과가 아니다!)
           {
             'loss_classifier' : 박스 헤드의 분류 손실
             'loss_box_reg'    : 박스 좌표 회귀 손실
             'loss_mask'       : 마스크 헤드의 픽셀 단위 BCE 손실
             'loss_objectness' : RPN이 "객체 유무"를 맞추는 손실
             'loss_rpn_box_reg': RPN의 후보 박스 회귀 손실
           }

    model.eval() 상태에서 model(images) 호출
        -> 예측 결과 list 를 반환한다. (loss가 아니다!)
           [{'boxes':..., 'labels':..., 'scores':..., 'masks':...}, ...]

    즉, 손실 함수를 우리가 따로 정의하지 않는다. 모델이 내부에서 계산해 준다.
    이것이 일반적인 `criterion(outputs, targets)` 패턴과 가장 다른 부분이다.
"""

from __future__ import annotations

import math
import sys
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from utils import MetricLogger, build_warmup_scheduler, move_targets_to_device


# ======================================================================
# 1) 학습 루프 (1 epoch)
# ======================================================================
def train_one_epoch(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    data_loader: DataLoader,
    device: torch.device,
    epoch: int,
    print_freq: int = 10,
    warmup_iters: int = 0,
    clip_grad_norm: float = 0.0,
    scaler: torch.cuda.amp.GradScaler | None = None,
) -> Dict[str, float]:
    """
    한 epoch 동안 모델을 학습시킨다.

    Returns:
        이번 epoch의 평균 손실들을 담은 dict
    """
    # ------------------------------------------------------------------
    # [단계 0] 학습 모드로 전환
    #   - BatchNorm이 배치 통계를 갱신하고, Dropout이 활성화된다.
    #   - torchvision detection 모델에서는 "loss를 반환하는 모드"가 된다는 뜻이기도 하다.
    # ------------------------------------------------------------------
    model.train()

    logger = MetricLogger(delimiter="  ")
    header = f"[Train] Epoch {epoch}"

    # ------------------------------------------------------------------
    # [단계 0-1] warm-up 스케줄러 준비 (첫 epoch에서만)
    #   초반 lr을 아주 작게 시작해 서서히 올린다. 발산 방지용.
    # ------------------------------------------------------------------
    warmup_scheduler = None
    if epoch == 0 and warmup_iters > 0:
        warmup_scheduler = build_warmup_scheduler(
            optimizer, warmup_iters=min(warmup_iters, len(data_loader) - 1)
        )

    for images, targets in logger.log_every(data_loader, print_freq, header):
        # --------------------------------------------------------------
        # [단계 1] 데이터를 연산 장치(GPU/CPU)로 옮긴다.
        #   images는 크기가 제각각인 텐서들의 튜플이므로 하나씩 옮긴다.
        #   targets는 dict의 리스트이므로 헬퍼로 옮긴다.
        # --------------------------------------------------------------
        images = [img.to(device) for img in images]
        targets = move_targets_to_device(targets, device)

        # --------------------------------------------------------------
        # [단계 2] Forward — 모델이 손실을 직접 계산해 dict로 돌려준다.
        #   autocast는 AMP(혼합정밀도) 사용 시 float16 연산으로 속도를 높인다.
        # --------------------------------------------------------------
        with torch.cuda.amp.autocast(enabled=scaler is not None):
            loss_dict: Dict[str, torch.Tensor] = model(images, targets)

            # --------------------------------------------------------------
            # [단계 3] 5개의 손실을 모두 더해 최종 스칼라 loss를 만든다.
            #   Mask R-CNN은 멀티태스크 학습이다:
            #     L = L_cls + L_box + L_mask + L_rpn_obj + L_rpn_box
            #   기본은 단순 합(가중치 1.0)이며, 특정 태스크를 강조하고 싶다면
            #   여기서 항별 가중치를 곱하면 된다.
            # --------------------------------------------------------------
            losses = sum(loss for loss in loss_dict.values())

        loss_value = losses.item()

        # --------------------------------------------------------------
        # [단계 3-1] 손실 발산(NaN/Inf) 방어
        #   Detection 학습은 lr이 조금만 커도 NaN으로 터진다.
        #   터진 상태로 계속 돌면 시간만 낭비하므로 즉시 멈추고 원인을 보여 준다.
        # --------------------------------------------------------------
        if not math.isfinite(loss_value):
            print(f"\n[오류] loss가 발산했습니다 (loss={loss_value}). 학습을 중단합니다.")
            print("  항목별 손실:", {k: v.item() for k, v in loss_dict.items()})
            print("  해결 방법: learning rate를 낮추거나 warmup_iters를 늘려 보세요.")
            sys.exit(1)

        # --------------------------------------------------------------
        # [단계 4] Backward — 역전파 3단계
        #   (1) zero_grad : 이전 step의 gradient를 지운다.
        #                   PyTorch는 gradient를 "누적"하므로 지우지 않으면 섞인다.
        #   (2) backward  : 손실로부터 각 파라미터의 gradient를 계산한다.
        #   (3) step      : 계산된 gradient로 파라미터를 갱신한다.
        # --------------------------------------------------------------
        optimizer.zero_grad(set_to_none=True)  # set_to_none=True가 약간 더 빠르고 메모리 효율적

        if scaler is not None:
            # AMP 사용 시: loss를 스케일 업해 float16에서 gradient가 0으로
            # 언더플로되는 것을 막는다.
            scaler.scale(losses).backward()
            if clip_grad_norm > 0:
                scaler.unscale_(optimizer)  # 클리핑 전에 원래 스케일로 되돌린다
                torch.nn.utils.clip_grad_norm_(model.parameters(), clip_grad_norm)
            scaler.step(optimizer)
            scaler.update()
        else:
            losses.backward()
            if clip_grad_norm > 0:
                # gradient의 전체 norm이 임계값을 넘으면 비율에 맞춰 줄인다.
                torch.nn.utils.clip_grad_norm_(model.parameters(), clip_grad_norm)
            optimizer.step()

        # --------------------------------------------------------------
        # [단계 5] warm-up 스케줄러는 iteration마다 갱신한다.
        #   (epoch 단위 스케줄러는 train.py의 바깥 루프에서 step 한다)
        # --------------------------------------------------------------
        if warmup_scheduler is not None:
            warmup_scheduler.step()

        # --------------------------------------------------------------
        # [단계 6] 로깅
        # --------------------------------------------------------------
        logger.update(loss=loss_value, **{k: v.item() for k, v in loss_dict.items()})
        logger.update(lr=optimizer.param_groups[0]["lr"])

    # 이번 epoch의 전체 평균값을 정리해 반환한다.
    return {name: meter.global_avg for name, meter in logger.meters.items()}


# ======================================================================
# 2) 검증 손실 계산
# ======================================================================
@torch.no_grad()
def evaluate_loss(
    model: nn.Module,
    data_loader: DataLoader,
    device: torch.device,
    print_freq: int = 10,
) -> Dict[str, float]:
    """
    검증 데이터에 대한 손실을 계산한다.

    [까다로운 부분]
        loss를 얻으려면 model.train() 모드여야 하는데,
        그러면 BatchNorm 통계가 검증 데이터로 오염된다.

        torchvision의 Mask R-CNN(ResNet-50 backbone)은 기본적으로
        FrozenBatchNorm2d를 사용하므로 통계가 갱신되지 않아 대체로 안전하다.
        그래도 안전하게 하려면 아래처럼 @torch.no_grad()로 감싸
        gradient 계산과 파라미터 갱신을 완전히 차단한다.

        ※ 정식 성능 지표(mAP)는 evaluate_map()으로 따로 측정한다.
    """
    was_training = model.training
    model.train()  # loss를 얻기 위해 일시적으로 train 모드

    logger = MetricLogger(delimiter="  ")
    header = "[Val]  "

    for images, targets in logger.log_every(data_loader, print_freq, header):
        images = [img.to(device) for img in images]
        targets = move_targets_to_device(targets, device)

        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())

        logger.update(loss=losses.item(), **{k: v.item() for k, v in loss_dict.items()})

    if not was_training:
        model.eval()  # 원래 모드로 복원

    return {name: meter.global_avg for name, meter in logger.meters.items()}


# ======================================================================
# 3) 성능 지표(mAP) 계산
# ======================================================================
def _box_iou(boxes_a: torch.Tensor, boxes_b: torch.Tensor) -> torch.Tensor:
    """
    두 박스 집합 간의 IoU(Intersection over Union) 행렬을 계산한다.

    IoU = (겹치는 영역 넓이) / (합집합 영역 넓이)
    값이 1에 가까울수록 두 박스가 정확히 겹친다는 뜻.

    Args:
        boxes_a: [N, 4]
        boxes_b: [M, 4]
    Returns:
        [N, M] IoU 행렬
    """
    if boxes_a.numel() == 0 or boxes_b.numel() == 0:
        return torch.zeros((boxes_a.shape[0], boxes_b.shape[0]), device=boxes_a.device)

    area_a = (boxes_a[:, 2] - boxes_a[:, 0]) * (boxes_a[:, 3] - boxes_a[:, 1])
    area_b = (boxes_b[:, 2] - boxes_b[:, 0]) * (boxes_b[:, 3] - boxes_b[:, 1])

    # 브로드캐스팅으로 모든 조합의 교집합 좌표를 한 번에 구한다.
    lt = torch.max(boxes_a[:, None, :2], boxes_b[None, :, :2])   # 좌상단은 더 큰 쪽
    rb = torch.min(boxes_a[:, None, 2:], boxes_b[None, :, 2:])   # 우하단은 더 작은 쪽

    wh = (rb - lt).clamp(min=0)                 # 음수면 겹치지 않음 -> 0
    inter = wh[:, :, 0] * wh[:, :, 1]

    union = area_a[:, None] + area_b[None, :] - inter
    return inter / union.clamp(min=1e-6)


@torch.no_grad()
def evaluate_map(
    model: nn.Module,
    data_loader: DataLoader,
    device: torch.device,
    iou_threshold: float = 0.5,
    score_threshold: float = 0.05,
) -> Dict[str, float]:
    """
    간이 mAP@IoU 계산기 (박스 기준).

    [왜 직접 구현했는가?]
        정식 COCO 평가는 pycocotools가 필요하고 코드가 길다.
        여기서는 "mAP가 어떻게 계산되는지" 흐름을 이해하는 것이 목적이므로
        단일 IoU 임계값 기준의 간단한 버전을 구현한다.

    [계산 흐름]
        1) 모든 이미지에 대해 예측을 모은다.
        2) 신뢰도(score) 순으로 전체 예측을 정렬한다.
        3) 높은 점수부터 순회하며 GT와 IoU >= threshold 이고 아직 매칭되지 않은
           GT가 있으면 TP(정답), 아니면 FP(오답)로 표시한다.
        4) 누적 TP/FP로 precision-recall 곡선을 그리고 그 아래 면적(AP)을 구한다.
        5) 클래스별 AP를 평균 내면 mAP.
    """
    model.eval()  # 예측 결과를 얻기 위해 eval 모드

    # 클래스별로 예측과 GT를 모아 둔다.
    predictions_by_class: Dict[int, List[Tuple[float, int, int]]] = {}  # (score, img_idx, box_idx)
    pred_boxes_by_class: Dict[int, Dict[int, torch.Tensor]] = {}
    gt_boxes_by_class: Dict[int, Dict[int, torch.Tensor]] = {}
    num_gt_by_class: Dict[int, int] = {}

    # ------------------------------------------------------------------
    # [단계 1] 전체 데이터셋에 대한 예측 수집
    # ------------------------------------------------------------------
    image_counter = 0  # 배치 크기가 달라져도 겹치지 않는 전역 이미지 일련번호

    for images, targets in data_loader:
        images = [img.to(device) for img in images]

        # eval 모드에서는 targets 없이 호출 -> 예측 결과 list 반환
        outputs = model(images)

        for output, target in zip(outputs, targets):
            key = image_counter          # 이미지 고유 키
            image_counter += 1

            # --- GT 정리 ---
            gt_labels = target["labels"]
            gt_boxes = target["boxes"]
            for cls in gt_labels.unique().tolist():
                mask = gt_labels == cls
                gt_boxes_by_class.setdefault(cls, {})[key] = gt_boxes[mask].to(device)
                num_gt_by_class[cls] = num_gt_by_class.get(cls, 0) + int(mask.sum())

            # --- 예측 정리 (낮은 점수는 버려 계산량을 줄인다) ---
            keep = output["scores"] >= score_threshold
            p_boxes = output["boxes"][keep]
            p_labels = output["labels"][keep]
            p_scores = output["scores"][keep]

            for cls in p_labels.unique().tolist():
                mask = p_labels == cls
                boxes_c = p_boxes[mask]
                scores_c = p_scores[mask]
                pred_boxes_by_class.setdefault(cls, {})[key] = boxes_c
                predictions_by_class.setdefault(cls, []).extend(
                    (float(s), key, i) for i, s in enumerate(scores_c.tolist())
                )

    # ------------------------------------------------------------------
    # [단계 2] 클래스별 AP 계산
    # ------------------------------------------------------------------
    aps: Dict[int, float] = {}

    for cls, preds in predictions_by_class.items():
        total_gt = num_gt_by_class.get(cls, 0)
        if total_gt == 0:
            continue  # GT가 없는 클래스는 AP를 정의할 수 없다

        # 신뢰도 내림차순 정렬 — mAP의 핵심 전제
        preds.sort(key=lambda x: -x[0])

        matched: Dict[int, set] = {}  # 이미지별로 이미 매칭된 GT 인덱스
        tp = torch.zeros(len(preds))
        fp = torch.zeros(len(preds))

        for i, (_score, img_key, box_i) in enumerate(preds):
            pred_box = pred_boxes_by_class[cls][img_key][box_i:box_i + 1]
            gts = gt_boxes_by_class.get(cls, {}).get(img_key)

            if gts is None or gts.numel() == 0:
                fp[i] = 1  # 그 이미지에 해당 클래스 GT가 없음 -> 무조건 오답
                continue

            ious = _box_iou(pred_box, gts)[0]           # [num_gt]
            best_iou, best_idx = ious.max(0)
            best_idx = int(best_idx)

            already = matched.setdefault(img_key, set())
            if best_iou >= iou_threshold and best_idx not in already:
                tp[i] = 1
                already.add(best_idx)  # 하나의 GT는 한 번만 매칭 (중복 검출은 FP)
            else:
                fp[i] = 1

        # --- precision-recall 곡선 ---
        cum_tp = torch.cumsum(tp, dim=0)
        cum_fp = torch.cumsum(fp, dim=0)
        recall = cum_tp / total_gt
        precision = cum_tp / (cum_tp + cum_fp).clamp(min=1e-6)

        # 단조 감소 보정: 오른쪽에서 왼쪽으로 최댓값을 전파한다.
        # (COCO/VOC 평가의 표준 절차. PR 곡선의 톱니 모양을 제거)
        for i in range(len(precision) - 2, -1, -1):
            precision[i] = max(precision[i], precision[i + 1])

        # 곡선 아래 면적을 사다리꼴이 아닌 직사각형 합으로 근사
        recall = torch.cat([torch.tensor([0.0]), recall])
        precision = torch.cat([torch.tensor([precision[0].item()]), precision])
        ap = float(((recall[1:] - recall[:-1]) * precision[1:]).sum())
        aps[cls] = ap

    mean_ap = float(sum(aps.values()) / len(aps)) if aps else 0.0

    result = {f"AP@{iou_threshold}_class{c}": v for c, v in sorted(aps.items())}
    result[f"mAP@{iou_threshold}"] = mean_ap
    return result
