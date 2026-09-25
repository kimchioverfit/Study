"""
visualize.py
============
[역할] 데이터셋의 정답(GT)이나 모델의 예측 결과를 이미지 위에 그려 저장한다.

[왜 시각화가 학습만큼 중요한가?]
    Detection/Segmentation에서 가장 흔한 실수는 loss 코드가 아니라
    **데이터 준비 단계의 좌표 규약 오류**다.
    - 박스가 (x, y, w, h)인지 (x1, y1, x2, y2)인지
    - 좌표가 정규화되어 있는지 절대 픽셀인지
    - 증강 후 마스크와 박스가 여전히 일치하는지

    이런 실수는 loss 값만 봐서는 절대 알 수 없고, 그림으로 그려 보면 즉시 보인다.
    **학습을 시작하기 전에 반드시 GT 시각화를 한 번 확인하는 습관**을 들이자.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch
from PIL import Image, ImageDraw

# 클래스별 구분 색상 (인덱스 0은 배경이라 쓰이지 않음)
PALETTE = [
    (0, 0, 0),
    (255, 60, 60),
    (60, 160, 255),
    (60, 220, 120),
    (255, 190, 60),
    (200, 100, 255),
]


def _tensor_to_pil(image: torch.Tensor) -> Image.Image:
    """
    [C, H, W] float 텐서(0~1)를 PIL 이미지로 되돌린다.
    ToTensor의 역연산이라고 보면 된다.
    """
    array = (image.detach().cpu().clamp(0, 1).permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return Image.fromarray(array)


def draw_instances(
    image: torch.Tensor,
    boxes: torch.Tensor,
    labels: torch.Tensor,
    masks: Optional[torch.Tensor] = None,
    scores: Optional[torch.Tensor] = None,
    class_names: Sequence[str] = (),
    mask_alpha: float = 0.45,
) -> Image.Image:
    """
    이미지 한 장 위에 박스 + 마스크 + 라벨을 그린다.

    Args:
        image  : [C, H, W] 0~1 텐서
        boxes  : [N, 4] (x1, y1, x2, y2)
        labels : [N] 클래스 인덱스
        masks  : [N, H, W] 이진 마스크 (float 확률맵이면 0.5로 이진화)
        scores : [N] 신뢰도 (예측 결과일 때만)
    """
    pil = _tensor_to_pil(image).convert("RGB")
    base = np.array(pil).astype(np.float32)

    # ------------------------------------------------------------------
    # [단계 1] 마스크를 반투명 색으로 덮어씌운다.
    #   합성 공식: 결과 = 원본*(1-alpha) + 색상*alpha
    #   마스크가 있는 픽셀에만 적용한다.
    # ------------------------------------------------------------------
    if masks is not None and masks.numel() > 0:
        m = masks.detach().cpu()
        if m.dtype.is_floating_point:
            # 예측 마스크는 [N, 1, H, W] 확률맵으로 나오므로 차원을 줄이고 이진화한다.
            m = m.squeeze(1) if m.dim() == 4 else m
            m = (m > 0.5)
        m = m.numpy().astype(bool)

        for i in range(m.shape[0]):
            color = np.array(PALETTE[int(labels[i]) % len(PALETTE)], dtype=np.float32)
            region = m[i]
            base[region] = base[region] * (1 - mask_alpha) + color * mask_alpha

    out = Image.fromarray(base.astype(np.uint8))
    draw = ImageDraw.Draw(out)

    # ------------------------------------------------------------------
    # [단계 2] 박스와 텍스트를 그린다.
    # ------------------------------------------------------------------
    for i in range(len(boxes)):
        x1, y1, x2, y2 = [float(v) for v in boxes[i].tolist()]
        cls = int(labels[i])
        color = PALETTE[cls % len(PALETTE)]

        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        name = class_names[cls] if cls < len(class_names) else str(cls)
        text = f"{name}" if scores is None else f"{name} {float(scores[i]):.2f}"

        # 텍스트 배경을 칠해 글자가 배경에 묻히지 않게 한다.
        draw.rectangle([x1, max(0, y1 - 12), x1 + 8 * len(text), y1], fill=color)
        draw.text((x1 + 2, max(0, y1 - 12)), text, fill=(255, 255, 255))

    return out


def save_dataset_samples(
    dataset,
    out_dir: str,
    class_names: Sequence[str],
    num_samples: int = 4,
) -> None:
    """
    학습 시작 전 "데이터가 제대로 만들어졌는지" 확인하기 위한 GT 시각화.
    outputs/gt_samples/ 에 이미지를 저장한다.
    """
    os.makedirs(out_dir, exist_ok=True)
    n = min(num_samples, len(dataset))

    for i in range(n):
        image, target = dataset[i]
        vis = draw_instances(
            image,
            target["boxes"],
            target["labels"],
            masks=target["masks"],
            class_names=class_names,
        )
        vis.save(os.path.join(out_dir, f"gt_{i:03d}.png"))

    print(f"[시각화] GT 샘플 {n}장을 {out_dir} 에 저장했습니다.")


@torch.no_grad()
def save_prediction_samples(
    model: torch.nn.Module,
    dataset,
    device: torch.device,
    out_dir: str,
    class_names: Sequence[str],
    score_threshold: float = 0.5,
    num_samples: int = 4,
) -> None:
    """
    학습된 모델의 예측 결과를 시각화해 저장한다.

    [예측 결과 dict 구조 — eval 모드일 때]
        boxes  : [N, 4]        신뢰도 내림차순으로 이미 정렬되어 있음
        labels : [N]
        scores : [N]           0~1 신뢰도
        masks  : [N, 1, H, W]  0~1 확률맵 (이진 마스크가 아님에 주의!)
                               보통 0.5를 임계값으로 이진화해서 쓴다.
    """
    os.makedirs(out_dir, exist_ok=True)
    model.eval()
    n = min(num_samples, len(dataset))

    for i in range(n):
        image, _ = dataset[i]
        output: Dict[str, torch.Tensor] = model([image.to(device)])[0]

        # 신뢰도가 낮은 예측은 걸러 낸다.
        keep = output["scores"] >= score_threshold
        vis = draw_instances(
            image,
            output["boxes"][keep].cpu(),
            output["labels"][keep].cpu(),
            masks=output["masks"][keep].cpu(),
            scores=output["scores"][keep].cpu(),
            class_names=class_names,
        )
        vis.save(os.path.join(out_dir, f"pred_{i:03d}.png"))

    print(f"[시각화] 예측 결과 {n}장을 {out_dir} 에 저장했습니다.")
