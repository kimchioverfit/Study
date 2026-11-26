"""
config.py
=========
[역할] 학습에 필요한 모든 "설정값(하이퍼파라미터)"을 한 곳에 모아두는 모듈.

[왜 분리하는가?]
    - 학습 코드(train.py) 안에 숫자가 흩어져 있으면 실험을 반복할 때 어디를 고쳐야
      하는지 찾기 어렵다.
    - 설정을 dataclass 하나로 모아두면 (1) 실험 재현이 쉽고, (2) 로그/체크포인트에
      설정을 통째로 저장해 둘 수 있으며, (3) CLI 인자로 덮어쓰기가 쉽다.

[사용법]
    from config import Config
    cfg = Config()                 # 기본값
    cfg = Config(num_epochs=20)    # 일부만 변경
"""

from dataclasses import dataclass, asdict
from typing import Tuple
import json


@dataclass
class Config:
    # ------------------------------------------------------------------
    # 1) 데이터 관련 설정
    # ------------------------------------------------------------------
    data_root: str = "data"
    # 데이터셋 루트 디렉터리.
    # 구조는 아래와 같다고 가정한다 (PennFudan 형식과 동일).
    #   data/
    #     images/  0000.png, 0001.png, ...
    #     masks/   0000.png, 0001.png, ...   <- 인스턴스마다 다른 정수값을 가진 마스크

    num_classes: int = 3
    # 클래스 개수 = "배경(background) 1개" + "실제 객체 클래스 개수".
    # 예) 객체가 circle, rectangle 2종류라면 -> 1 + 2 = 3.
    # Mask R-CNN의 분류 헤드는 항상 배경 클래스를 0번으로 포함해야 한다.

    class_names: Tuple[str, ...] = ("__background__", "circle", "rectangle")
    # 시각화/로그 출력을 위한 사람이 읽을 수 있는 클래스 이름. 인덱스 0은 배경.

    val_ratio: float = 0.2
    # 전체 데이터 중 검증(validation)으로 떼어낼 비율.

    # ------------------------------------------------------------------
    # 2) DataLoader 관련 설정
    # ------------------------------------------------------------------
    batch_size: int = 2
    # Detection 모델은 이미지 한 장당 메모리 사용량이 크므로 batch_size가 작다.
    # (일반적으로 GPU 1장 기준 2~8 정도)

    num_workers: int = 0
    # 데이터 로딩에 사용할 서브프로세스 수.
    # Windows에서는 num_workers > 0 일 때 반드시 `if __name__ == "__main__":`
    # 가드 안에서 실행해야 한다. 학습용 샘플이므로 안전하게 0으로 둔다.

    # ------------------------------------------------------------------
    # 3) 모델 관련 설정
    # ------------------------------------------------------------------
    backbone_pretrained: bool = True
    # ImageNet으로 사전학습된 ResNet-50 백본 가중치를 사용할지 여부.
    # 인터넷 연결이 없다면 False로 두면 랜덤 초기화로 진행된다.

    trainable_backbone_layers: int = 3
    # 백본(ResNet)의 마지막 몇 개 stage를 학습시킬지 (0~5).
    # 데이터가 적을수록 작은 값(=대부분 freeze)이 과적합 방지에 유리하다.

    hidden_layer_mask_head: int = 256
    # Mask 예측 헤드 내부 conv 채널 수. torchvision 기본값도 256.

    # ------------------------------------------------------------------
    # 4) 최적화(Optimizer / Scheduler) 관련 설정
    # ------------------------------------------------------------------
    optimizer: str = "sgd"          # "sgd" 또는 "adamw"
    lr: float = 0.005               # 기본 학습률
    momentum: float = 0.9           # SGD 전용
    weight_decay: float = 5e-4      # 가중치 감쇠(L2 정규화)

    lr_scheduler: str = "steplr"    # "steplr" | "cosine" | "none"
    lr_step_size: int = 3           # StepLR: 몇 epoch마다 lr을 줄일지
    lr_gamma: float = 0.1           # StepLR: 줄일 비율

    warmup_iters: int = 100
    # 학습 초반에는 lr을 0에서부터 서서히 올린다(warm-up).
    # Detection 모델은 초기 loss가 매우 크기 때문에 warm-up이 없으면 발산하기 쉽다.

    clip_grad_norm: float = 10.0
    # gradient 폭발 방지용 클리핑 임계값. 0 이하이면 클리핑하지 않음.

    # ------------------------------------------------------------------
    # 5) 학습 루프 관련 설정
    # ------------------------------------------------------------------
    num_epochs: int = 5
    print_freq: int = 10            # 몇 iteration마다 로그를 찍을지
    amp: bool = False               # Mixed Precision(FP16) 사용 여부 (CUDA에서만 유효)
    seed: int = 42                  # 재현성을 위한 랜덤 시드

    # ------------------------------------------------------------------
    # 6) 출력 관련 설정
    # ------------------------------------------------------------------
    output_dir: str = "outputs"     # 체크포인트/로그/시각화 결과 저장 위치
    save_every: int = 1             # 몇 epoch마다 체크포인트를 저장할지
    score_threshold: float = 0.5    # 추론 결과 시각화 시 사용할 신뢰도 임계값

    # ------------------------------------------------------------------
    # 유틸리티
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """설정을 dict로 변환 (체크포인트에 함께 저장할 때 사용)."""
        return asdict(self)

    def save(self, path: str) -> None:
        """설정을 JSON 파일로 저장해 실험 재현성을 확보한다."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def __str__(self) -> str:
        lines = ["Config:"]
        for k, v in self.to_dict().items():
            lines.append(f"  - {k:28s}: {v}")
        return "\n".join(lines)
