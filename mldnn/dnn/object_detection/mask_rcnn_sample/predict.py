"""
predict.py
==========
[역할] 학습이 끝난 체크포인트를 불러와 새 이미지에 대해 추론(inference)만 수행한다.

[학습 코드와 분리하는 이유]
    실제 서비스나 배포 환경에서는 데이터 증강, 옵티마이저, 손실 계산이 전혀 필요 없다.
    추론 경로를 별도 파일로 분리해 두면 의존성이 줄고, 무엇이 필수인지 명확해진다.

[추론 시 반드시 지켜야 할 3가지]
    1) model.eval()            : BatchNorm/Dropout을 평가 모드로 전환
    2) torch.no_grad()         : gradient 계산을 꺼서 메모리/속도 확보
    3) 학습과 동일한 전처리     : 여기서는 ToTensor만 (정규화는 모델 내부에서 수행)

실행:
    python predict.py --checkpoint outputs/best_model.pth --input data/images/0000.png
    python predict.py --checkpoint outputs/best_model.pth --input data/images --out-dir results
"""

from __future__ import annotations

import argparse
import os
from typing import Dict, List

import torch
from PIL import Image

from config import Config
from model import build_model
from utils import get_device
from visualize import draw_instances

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def load_model_from_checkpoint(
    checkpoint_path: str, device: torch.device, num_classes: int
) -> torch.nn.Module:
    """
    체크포인트에서 모델을 복원한다.

    [주의] state_dict만으로는 모델 구조를 알 수 없다.
           따라서 학습 때와 **완전히 동일한 구조**로 모델을 먼저 만든 뒤
           가중치를 얹어야 한다. 그래서 체크포인트에 config를 함께 저장해 둔 것이다.
    """
    checkpoint = torch.load(checkpoint_path, map_location=device)

    # 체크포인트에 config가 들어 있으면 그 값을 우선 사용한다.
    saved_config = checkpoint.get("config", {})
    num_classes = saved_config.get("num_classes", num_classes)

    # pretrained=False: 어차피 학습된 가중치로 덮어쓸 것이므로 다운로드가 불필요하다.
    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model"])
    model.to(device)
    model.eval()   # 필수: 이 호출이 있어야 예측 결과를 반환한다

    print(f"[모델 로드] {checkpoint_path} (epoch {checkpoint.get('epoch')}, "
          f"num_classes={num_classes})")
    return model


@torch.no_grad()   # 이 함수 전체에서 gradient 계산을 끈다
def predict_single_image(
    model: torch.nn.Module,
    image_path: str,
    device: torch.device,
    score_threshold: float = 0.5,
):
    """
    이미지 한 장에 대해 추론을 수행한다.

    Returns:
        (image_tensor, 필터링된 예측 dict)
    """
    # --- 전처리: 학습 때와 동일해야 한다 ---
    import torchvision.transforms.functional as F

    pil_image = Image.open(image_path).convert("RGB")
    image_tensor = F.to_tensor(pil_image)   # [C, H, W], 0~1

    # --- 추론: 리스트로 감싸서 넘긴다 (배치 차원 역할) ---
    output: Dict[str, torch.Tensor] = model([image_tensor.to(device)])[0]

    # --- 후처리: 신뢰도 임계값으로 걸러내기 ---
    #   모델은 이미 NMS(Non-Maximum Suppression)를 내부에서 수행한 결과를 준다.
    #   여기서는 점수가 낮은 예측만 추가로 제거하면 된다.
    keep = output["scores"] >= score_threshold
    filtered = {
        "boxes": output["boxes"][keep].cpu(),
        "labels": output["labels"][keep].cpu(),
        "scores": output["scores"][keep].cpu(),
        "masks": output["masks"][keep].cpu(),   # [N, 1, H, W] 확률맵
    }
    return image_tensor, filtered


def collect_image_paths(input_path: str) -> List[str]:
    """입력이 파일이면 그 하나, 디렉터리면 안의 모든 이미지를 반환한다."""
    if os.path.isfile(input_path):
        return [input_path]
    return sorted(
        os.path.join(input_path, f)
        for f in os.listdir(input_path)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mask R-CNN 추론 스크립트")
    parser.add_argument("--checkpoint", type=str, required=True, help="체크포인트 경로")
    parser.add_argument("--input", type=str, required=True, help="이미지 파일 또는 디렉터리")
    parser.add_argument("--out-dir", type=str, default="outputs/inference")
    parser.add_argument("--score-threshold", type=float, default=0.5)
    args = parser.parse_args()

    cfg = Config()
    device = get_device()
    os.makedirs(args.out_dir, exist_ok=True)

    model = load_model_from_checkpoint(args.checkpoint, device, cfg.num_classes)

    image_paths = collect_image_paths(args.input)
    print(f"[추론 시작] 이미지 {len(image_paths)}장")

    for path in image_paths:
        image_tensor, pred = predict_single_image(
            model, path, device, args.score_threshold
        )

        vis = draw_instances(
            image_tensor,
            pred["boxes"],
            pred["labels"],
            masks=pred["masks"],
            scores=pred["scores"],
            class_names=cfg.class_names,
        )

        stem = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(args.out_dir, f"{stem}_pred.png")
        vis.save(out_path)

        print(f"  {os.path.basename(path)}: 객체 {len(pred['boxes'])}개 검출 -> {out_path}")

    print(f"\n[완료] 결과가 '{args.out_dir}' 에 저장되었습니다.")


if __name__ == "__main__":
    main()
