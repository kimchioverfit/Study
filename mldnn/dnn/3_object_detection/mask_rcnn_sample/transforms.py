"""
transforms.py
=============
[역할] 데이터 증강(Data Augmentation) 및 전처리 파이프라인.

[Classification과 무엇이 다른가?]
    분류 문제에서는 이미지만 변형하면 되지만, Detection/Segmentation에서는
    이미지를 뒤집거나 자르면 **정답(bounding box, mask)도 같이 변형**해야 한다.
    그래서 torchvision의 일반 transform을 그대로 쓸 수 없고,
    (image, target)을 함께 받아 함께 변형하는 transform을 직접 정의한다.

[의도적으로 외부 의존성을 쓰지 않은 이유]
    albumentations 등을 쓰면 편하지만, 여기서는 "박스와 마스크가 어떻게 함께
    변형되는지"를 눈으로 확인하는 것이 목적이므로 직접 구현한다.
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

import torch
import torchvision.transforms.functional as F


# ======================================================================
# 기본 골격
# ======================================================================
class Compose:
    """
    여러 transform을 순서대로 적용하는 컨테이너.
    torchvision.transforms.Compose와 동일한 개념이지만
    (image, target) 두 개를 함께 넘긴다는 점이 다르다.
    """

    def __init__(self, transforms: List):
        self.transforms = transforms

    def __call__(self, image, target: Dict[str, torch.Tensor]):
        for t in self.transforms:
            image, target = t(image, target)
        return image, target


class ToTensor:
    """
    PIL.Image -> torch.Tensor 변환.

    - 결과 shape: [C, H, W]
    - 값 범위: 0~255 정수 -> 0.0~1.0 실수로 자동 정규화
    - 평균/표준편차 정규화(Normalize)는 여기서 하지 않는다.
      torchvision의 Mask R-CNN은 모델 내부 GeneralizedRCNNTransform에서
      ImageNet 통계로 정규화 + 리사이즈를 수행하기 때문에,
      바깥에서 또 정규화하면 이중 적용이 되어 성능이 나빠진다.
    """

    def __call__(self, image, target):
        return F.to_tensor(image), target


# ======================================================================
# 기하학적 증강 (이미지 + target을 함께 변형)
# ======================================================================
class RandomHorizontalFlip:
    """
    확률 p로 좌우 반전을 수행한다.

    [함께 바뀌어야 하는 것]
        1) image : 좌우 반전
        2) masks : 좌우 반전 (마지막 차원 W를 뒤집음)
        3) boxes : x좌표를 W 기준으로 대칭 이동
                   새로운 x_min = W - 기존 x_max
                   새로운 x_max = W - 기존 x_min
                   (x_min < x_max 순서가 깨지지 않도록 min/max를 교환하는 것이 핵심)
    """

    def __init__(self, p: float = 0.5):
        self.p = p

    def __call__(self, image: torch.Tensor, target: Dict[str, torch.Tensor]):
        if random.random() >= self.p:
            return image, target

        # 이미지 텐서는 [C, H, W] -> 마지막 축(W)을 뒤집는다.
        width = image.shape[-1]
        image = image.flip(-1)

        # --- bounding box 좌표 변환 ---
        if "boxes" in target and target["boxes"].numel() > 0:
            boxes = target["boxes"].clone()          # [N, 4] = (x_min, y_min, x_max, y_max)
            x_min = boxes[:, 0].clone()
            x_max = boxes[:, 2].clone()
            boxes[:, 0] = width - x_max              # 새 x_min
            boxes[:, 2] = width - x_min              # 새 x_max
            target["boxes"] = boxes

        # --- 인스턴스 마스크 변환 ---
        if "masks" in target and target["masks"].numel() > 0:
            target["masks"] = target["masks"].flip(-1)  # [N, H, W]의 W축 반전

        return image, target


class RandomVerticalFlip:
    """상하 반전. 수평 반전과 동일한 논리를 y축에 적용한다."""

    def __init__(self, p: float = 0.5):
        self.p = p

    def __call__(self, image: torch.Tensor, target: Dict[str, torch.Tensor]):
        if random.random() >= self.p:
            return image, target

        height = image.shape[-2]
        image = image.flip(-2)  # H축 반전

        if "boxes" in target and target["boxes"].numel() > 0:
            boxes = target["boxes"].clone()
            y_min = boxes[:, 1].clone()
            y_max = boxes[:, 3].clone()
            boxes[:, 1] = height - y_max
            boxes[:, 3] = height - y_min
            target["boxes"] = boxes

        if "masks" in target and target["masks"].numel() > 0:
            target["masks"] = target["masks"].flip(-2)

        return image, target


# ======================================================================
# 색상 증강 (target은 변하지 않음)
# ======================================================================
class RandomPhotometricDistort:
    """
    밝기/대비/채도를 무작위로 흔들어 조명 변화에 강인하게 만든다.
    기하학적 위치를 바꾸지 않으므로 target은 그대로 둔다.
    """

    def __init__(
        self,
        brightness: Tuple[float, float] = (0.8, 1.2),
        contrast: Tuple[float, float] = (0.8, 1.2),
        saturation: Tuple[float, float] = (0.8, 1.2),
        p: float = 0.5,
    ):
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
        self.p = p

    def __call__(self, image: torch.Tensor, target):
        if random.random() >= self.p:
            return image, target

        image = F.adjust_brightness(image, random.uniform(*self.brightness))
        image = F.adjust_contrast(image, random.uniform(*self.contrast))
        image = F.adjust_saturation(image, random.uniform(*self.saturation))
        # 값이 [0, 1] 범위를 벗어날 수 있으므로 잘라 준다.
        return image.clamp(0.0, 1.0), target


# ======================================================================
# 팩토리 함수
# ======================================================================
def build_transforms(train: bool) -> Compose:
    """
    학습/검증 단계에 맞는 transform 파이프라인을 만들어 준다.

    [중요] 검증(validation)/추론(inference) 단계에서는 무작위 증강을 절대 넣지 않는다.
           평가 결과가 실행할 때마다 달라져 모델 비교가 불가능해지기 때문이다.
    """
    transforms: List = [ToTensor()]  # PIL -> Tensor 는 항상 필요

    if train:
        transforms.append(RandomHorizontalFlip(p=0.5))
        transforms.append(RandomPhotometricDistort(p=0.3))
        # 필요하면 RandomVerticalFlip 등을 추가한다.
        # 단, 데이터 특성상 말이 되는 증강만 넣어야 한다.
        # (예: 사람/글자 데이터에 상하 반전은 오히려 해롭다)

    return Compose(transforms)
