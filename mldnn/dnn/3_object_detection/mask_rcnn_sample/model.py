"""
model.py
========
[역할] Mask R-CNN 모델을 만들고, 우리 데이터셋에 맞게 "머리(head)"를 교체하는 모듈.

[Mask R-CNN 전체 구조 요약]

    입력 이미지
        |
        v
    (1) Transform      : 정규화 + 리사이즈 + 배치 패딩  (모델 내부에 포함되어 있음)
        |
        v
    (2) Backbone       : ResNet-50  -> 이미지에서 특징(feature) 추출
        |
        v
    (3) FPN            : Feature Pyramid Network
                         여러 해상도의 특징맵을 합쳐 작은 객체/큰 객체 모두 잘 잡게 함
        |
        v
    (4) RPN            : Region Proposal Network
                         "객체가 있을 법한 후보 영역(proposal)"을 대량으로 뽑아냄
                         loss: loss_objectness, loss_rpn_box_reg
        |
        v
    (5) RoIAlign       : 후보 영역을 고정 크기(7x7 / 14x14) 특징으로 잘라냄
        |
        +--------------------------+--------------------------+
        |                          |                          |
        v                          v                          v
    (6) Box Head              (7) Mask Head
        - 클래스 분류               - 픽셀 단위 이진 마스크 예측
        - 박스 좌표 회귀            loss: loss_mask
        loss: loss_classifier,
              loss_box_reg

[왜 head만 교체하는가? = Transfer Learning]
    torchvision이 제공하는 사전학습 가중치는 COCO 데이터셋(91개 클래스)으로 학습됐다.
    백본과 FPN이 학습한 "일반적인 시각 특징"은 우리 데이터에도 그대로 유용하지만,
    마지막 분류기는 91개 클래스 출력이라 우리 클래스 수와 맞지 않는다.
    따라서 **백본은 재사용하고 예측 head만 새 클래스 수에 맞게 갈아 끼운다.**
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor


# ======================================================================
# 사전학습 가중치 로드 (torchvision 버전 호환 처리)
# ======================================================================
def _load_base_maskrcnn(pretrained: bool, trainable_backbone_layers: int) -> nn.Module:
    """
    torchvision의 maskrcnn_resnet50_fpn 을 불러온다.

    torchvision 0.13부터 `pretrained=True` 대신 `weights=...` 방식으로 API가 바뀌었다.
    두 버전 모두에서 동작하도록 try/except로 감싼다.
    """
    try:
        # torchvision >= 0.13 (권장 방식)
        from torchvision.models.detection import (
            MaskRCNN_ResNet50_FPN_Weights,
        )

        weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT if pretrained else None
        model = torchvision.models.detection.maskrcnn_resnet50_fpn(
            weights=weights,
            # 백본 사전학습 가중치도 함께 지정 (weights를 쓰면 자동으로 따라온다)
            trainable_backbone_layers=trainable_backbone_layers,
        )
    except (ImportError, TypeError):
        # torchvision < 0.13 (구버전 fallback)
        model = torchvision.models.detection.maskrcnn_resnet50_fpn(
            pretrained=pretrained,
            trainable_backbone_layers=trainable_backbone_layers,
        )
    return model


# ======================================================================
# 메인 팩토리 함수
# ======================================================================
def build_model(
    num_classes: int,
    pretrained: bool = True,
    trainable_backbone_layers: int = 3,
    hidden_layer_mask_head: int = 256,
) -> nn.Module:
    """
    우리 데이터셋에 맞춘 Mask R-CNN 모델을 생성한다.

    Args:
        num_classes: 배경 포함 클래스 수 (예: 배경 + circle + rectangle = 3)
        pretrained:  COCO 사전학습 가중치 사용 여부
        trainable_backbone_layers: 백본에서 학습시킬 stage 수 (0~5)
        hidden_layer_mask_head: 마스크 예측 헤드의 중간 채널 수

    Returns:
        학습 준비가 끝난 nn.Module
    """
    # ------------------------------------------------------------------
    # [단계 1] 사전학습된 Mask R-CNN 뼈대를 그대로 가져온다.
    # ------------------------------------------------------------------
    model = _load_base_maskrcnn(pretrained, trainable_backbone_layers)

    # ------------------------------------------------------------------
    # [단계 2] Box Predictor 교체 (분류 + 박스 회귀 헤드)
    #
    #   기존 head의 입력 특징 차원(in_features)은 그대로 재사용하고,
    #   출력 차원만 우리 num_classes에 맞춰 새로 만든다.
    #
    #   FastRCNNPredictor 내부에는 두 개의 Linear가 있다.
    #     - cls_score  : [in_features] -> [num_classes]        (클래스 확률)
    #     - bbox_pred  : [in_features] -> [num_classes * 4]    (클래스별 박스 보정값)
    # ------------------------------------------------------------------
    in_features_box = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features_box, num_classes)

    # ------------------------------------------------------------------
    # [단계 3] Mask Predictor 교체 (픽셀 단위 마스크 헤드)
    #
    #   MaskRCNNPredictor 구조:
    #     ConvTranspose2d(in_ch -> hidden)  # 14x14 -> 28x28 로 업샘플링
    #     ReLU
    #     Conv2d(hidden -> num_classes, 1x1)  # 클래스마다 하나의 마스크를 예측
    #
    #   Mask R-CNN은 "클래스별로 각각 마스크를 예측"한 뒤,
    #   box head가 고른 클래스에 해당하는 마스크만 사용한다.
    #   (마스크 예측과 클래스 분류를 분리 = 논문의 핵심 아이디어 중 하나)
    # ------------------------------------------------------------------
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer_mask_head,
        num_classes,
    )

    return model


# ======================================================================
# 옵티마이저 / 스케줄러 팩토리
# ======================================================================
def build_optimizer(
    model: nn.Module,
    name: str = "sgd",
    lr: float = 0.005,
    momentum: float = 0.9,
    weight_decay: float = 5e-4,
) -> torch.optim.Optimizer:
    """
    옵티마이저를 만든다.

    [핵심] requires_grad=True 인 파라미터만 넘긴다.
           freeze된 백본 레이어까지 넘기면 불필요한 메모리를 잡아먹고,
           일부 옵티마이저는 경고나 오류를 낸다.
    """
    params = [p for p in model.parameters() if p.requires_grad]

    if name.lower() == "sgd":
        # Detection 모델의 전통적인 기본 선택. 큰 배치에서 안정적이다.
        return torch.optim.SGD(
            params, lr=lr, momentum=momentum, weight_decay=weight_decay
        )
    elif name.lower() == "adamw":
        # 데이터가 적거나 lr 튜닝이 귀찮을 때 무난하다.
        # 단, SGD와 같은 lr을 쓰면 발산하므로 보통 1/10 수준(예: 1e-4)으로 낮춘다.
        return torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay)
    else:
        raise ValueError(f"지원하지 않는 optimizer입니다: {name}")


def build_lr_scheduler(
    optimizer: torch.optim.Optimizer,
    name: str = "steplr",
    step_size: int = 3,
    gamma: float = 0.1,
    num_epochs: int = 10,
) -> Optional[object]:
    """
    epoch 단위로 동작하는 학습률 스케줄러를 만든다.
    (iteration 단위 warm-up 스케줄러는 utils.build_warmup_scheduler 참고)
    """
    name = name.lower()
    if name == "steplr":
        # step_size epoch마다 lr에 gamma를 곱한다. 가장 흔한 방식.
        return torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    elif name == "cosine":
        # 전체 학습 구간에 걸쳐 lr을 코사인 곡선으로 부드럽게 낮춘다.
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    elif name == "none":
        return None
    raise ValueError(f"지원하지 않는 scheduler입니다: {name}")


# ======================================================================
# 참고용: 모델 구조 훑어보기
# ======================================================================
def describe_model(model: nn.Module) -> str:
    """
    모델의 주요 구성 요소를 한눈에 보여 주는 문자열을 만든다.
    (전체 구조를 print하면 너무 길어서 학습에 방해가 되므로 요약본을 만든다)
    """
    lines = ["Mask R-CNN 구조 요약", "=" * 60]
    lines.append(f"  transform    : {type(model.transform).__name__}")
    lines.append(f"                 (min_size={model.transform.min_size}, "
                 f"max_size={model.transform.max_size})")
    lines.append(f"  backbone     : {type(model.backbone).__name__} (ResNet-50 + FPN)")
    lines.append(f"  rpn          : {type(model.rpn).__name__}")
    lines.append(f"  roi_heads    : {type(model.roi_heads).__name__}")
    lines.append(f"    ├ box_predictor  : {type(model.roi_heads.box_predictor).__name__} "
                 f"-> {model.roi_heads.box_predictor.cls_score.out_features} classes")
    lines.append(f"    └ mask_predictor : {type(model.roi_heads.mask_predictor).__name__} "
                 f"-> {model.roi_heads.mask_predictor.mask_fcn_logits.out_channels} classes")
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    # 이 파일을 단독 실행하면 모델 구조만 확인할 수 있다.
    m = build_model(num_classes=3, pretrained=False)
    print(describe_model(m))
