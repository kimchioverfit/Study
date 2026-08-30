"""
utils.py
========
[역할] 학습 파이프라인 어디에서나 쓰이는 "잡다하지만 꼭 필요한" 보조 함수 모음.

담고 있는 것:
    1) 재현성(seed) 고정
    2) 장치(device) 선택
    3) detection 전용 collate_fn
    4) 이동 평균 기반 로거 (SmoothedValue / MetricLogger)
    5) 체크포인트 저장/불러오기
    6) warm-up 학습률 스케줄러
"""

from __future__ import annotations

import os
import random
import time
from collections import defaultdict, deque
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch


# ======================================================================
# 1) 재현성 (Reproducibility)
# ======================================================================
def set_seed(seed: int = 42, deterministic: bool = False) -> None:
    """
    파이썬 / NumPy / PyTorch의 난수 생성기를 모두 같은 시드로 고정한다.

    [왜 필요한가?]
        가중치 초기화, 데이터 셔플, 데이터 증강 등 학습 곳곳에 난수가 쓰인다.
        시드를 고정하지 않으면 같은 코드도 실행할 때마다 결과가 달라져
        "내가 바꾼 하이퍼파라미터 덕분에 좋아진 것인지" 판단할 수 없다.

    Args:
        seed: 고정할 시드값
        deterministic: True면 cuDNN의 비결정적 알고리즘 사용을 금지한다.
                       완전한 재현성을 얻는 대신 학습 속도가 느려질 수 있다.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    else:
        # 입력 크기가 자주 바뀌지 않는다면 benchmark=True가 더 빠르다.
        torch.backends.cudnn.benchmark = True


# ======================================================================
# 2) 장치 선택
# ======================================================================
def get_device(prefer_cuda: bool = True) -> torch.device:
    """CUDA가 사용 가능하면 GPU를, 아니면 CPU를 반환한다."""
    if prefer_cuda and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# ======================================================================
# 3) Detection 전용 collate_fn
# ======================================================================
def collate_fn(batch: Sequence[Tuple[Any, Any]]) -> Tuple[Tuple, Tuple]:
    """
    DataLoader가 여러 샘플을 하나의 배치로 묶을 때 사용하는 함수.

    [왜 기본 collate를 못 쓰는가?]
        PyTorch의 기본 collate_fn은 배치 내 모든 텐서의 shape이 같다고 가정하고
        torch.stack()으로 쌓는다. 그러나 detection에서는
          - 이미지 크기가 서로 다를 수 있고,
          - 이미지마다 객체 개수가 달라 box/mask 텐서의 첫 번째 차원이 다르다.
        따라서 억지로 쌓지 않고 "튜플 그대로" 넘긴다.
        실제 크기 맞춤(padding)은 torchvision의 GeneralizedRCNNTransform이
        모델 내부에서 알아서 처리해 준다.

    Returns:
        (images, targets) 형태의 튜플.
        images  = (img1, img2, ...)   각 원소는 [C, H, W] 텐서
        targets = (tgt1, tgt2, ...)   각 원소는 dict
    """
    return tuple(zip(*batch))


# ======================================================================
# 4) 로깅 유틸리티
# ======================================================================
class SmoothedValue:
    """
    최근 N개 값의 이동 평균과 전체 평균을 함께 관리하는 작은 헬퍼.

    loss는 iteration마다 심하게 흔들리기 때문에 순간값만 보면 추세를 알 수 없다.
    최근 값들의 중앙값/평균을 보여주면 학습이 잘 되고 있는지 파악하기 쉽다.
    """

    def __init__(self, window_size: int = 20, fmt: str = "{median:.4f} ({global_avg:.4f})"):
        self.deque: deque = deque(maxlen=window_size)  # 최근 window_size개만 보관
        self.total = 0.0                               # 전체 합
        self.count = 0                                 # 전체 개수
        self.fmt = fmt

    def update(self, value: float, n: int = 1) -> None:
        self.deque.append(value)
        self.count += n
        self.total += value * n

    @property
    def median(self) -> float:
        return float(np.median(list(self.deque))) if self.deque else 0.0

    @property
    def avg(self) -> float:
        return float(np.mean(list(self.deque))) if self.deque else 0.0

    @property
    def global_avg(self) -> float:
        return self.total / self.count if self.count else 0.0

    def __str__(self) -> str:
        return self.fmt.format(median=self.median, avg=self.avg, global_avg=self.global_avg)


class MetricLogger:
    """
    여러 개의 SmoothedValue를 이름별로 관리하고,
    학습 루프를 감싸서 주기적으로 진행 상황을 출력해 주는 로거.

    사용 예)
        logger = MetricLogger(delimiter="  ")
        for images, targets in logger.log_every(data_loader, 10, header="Epoch [0]"):
            ...
            logger.update(loss=loss_value, lr=current_lr)
    """

    def __init__(self, delimiter: str = "  "):
        self.meters: Dict[str, SmoothedValue] = defaultdict(SmoothedValue)
        self.delimiter = delimiter

    def update(self, **kwargs: float) -> None:
        for k, v in kwargs.items():
            if isinstance(v, torch.Tensor):
                v = v.item()
            self.meters[k].update(float(v))

    def __str__(self) -> str:
        return self.delimiter.join(f"{name}: {meter}" for name, meter in self.meters.items())

    def log_every(self, iterable: Iterable, print_freq: int, header: str = ""):
        """
        iterable을 순회하면서 print_freq마다 현재 지표를 출력하는 제너레이터.
        학습 루프 코드에서 로깅 관련 코드를 걷어내 가독성을 높여 준다.
        """
        i = 0
        start_time = time.time()
        total = len(iterable) if hasattr(iterable, "__len__") else None

        for obj in iterable:
            yield obj
            i += 1
            if i % print_freq == 0 or i == total:
                elapsed = time.time() - start_time
                it_per_sec = i / elapsed if elapsed > 0 else 0.0
                progress = f"[{i}/{total}]" if total else f"[{i}]"
                print(f"{header} {progress}  {self}  ({it_per_sec:.2f} it/s)")

        total_time = time.time() - start_time
        print(f"{header} 완료 - 총 {total_time:.1f}초, {self}")


# ======================================================================
# 5) 체크포인트 저장 / 불러오기
# ======================================================================
def save_checkpoint(
    path: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    lr_scheduler: Any = None,
    epoch: int = 0,
    extra: Dict[str, Any] | None = None,
) -> None:
    """
    학습 상태를 파일로 저장한다.

    [모델 가중치만 저장하면 안 되는 이유]
        학습을 중간에 재개하려면 optimizer의 momentum 버퍼, scheduler의 step 수도
        함께 복원해야 이전과 동일한 궤적으로 이어서 학습할 수 있다.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    checkpoint = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "lr_scheduler": lr_scheduler.state_dict() if lr_scheduler is not None else None,
        "epoch": epoch,
    }
    if extra:
        checkpoint.update(extra)
    torch.save(checkpoint, path)
    print(f"[체크포인트 저장] {path}")


def load_checkpoint(
    path: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    lr_scheduler: Any = None,
    map_location: str | torch.device = "cpu",
) -> int:
    """저장된 체크포인트를 복원하고, 이어서 시작할 epoch 번호를 반환한다."""
    checkpoint = torch.load(path, map_location=map_location)
    model.load_state_dict(checkpoint["model"])

    if optimizer is not None and checkpoint.get("optimizer") is not None:
        optimizer.load_state_dict(checkpoint["optimizer"])
    if lr_scheduler is not None and checkpoint.get("lr_scheduler") is not None:
        lr_scheduler.load_state_dict(checkpoint["lr_scheduler"])

    start_epoch = int(checkpoint.get("epoch", 0)) + 1
    print(f"[체크포인트 로드] {path} (epoch {checkpoint.get('epoch')} 이후부터 재개)")
    return start_epoch


# ======================================================================
# 6) Warm-up 스케줄러
# ======================================================================
def build_warmup_scheduler(
    optimizer: torch.optim.Optimizer,
    warmup_iters: int,
    warmup_factor: float = 1.0 / 1000,
) -> torch.optim.lr_scheduler.LambdaLR | None:
    """
    학습 초반 warmup_iters 동안 학습률을 warmup_factor*lr -> lr 로 선형 증가시킨다.

    [왜 필요한가?]
        Mask R-CNN은 초기화 직후 RPN/ROI 헤드의 loss가 매우 크다.
        처음부터 큰 lr을 쓰면 첫 몇 step에서 가중치가 크게 튀어 NaN으로 발산한다.
        warm-up은 이 초기 구간을 부드럽게 지나가게 해 준다.

    Returns:
        LambdaLR 스케줄러. warmup_iters <= 0 이면 None.
    """
    if warmup_iters <= 0:
        return None

    def f(current_iter: int) -> float:
        if current_iter >= warmup_iters:
            return 1.0  # warm-up 종료 후에는 배율 1.0 (원래 lr)
        alpha = current_iter / warmup_iters
        return warmup_factor * (1 - alpha) + alpha

    return torch.optim.lr_scheduler.LambdaLR(optimizer, f)


# ======================================================================
# 7) 기타
# ======================================================================
def count_parameters(model: torch.nn.Module) -> Tuple[int, int]:
    """(전체 파라미터 수, 학습 가능한 파라미터 수)를 반환한다."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def move_targets_to_device(
    targets: Sequence[Dict[str, torch.Tensor]], device: torch.device
) -> List[Dict[str, torch.Tensor]]:
    """
    target dict 안의 모든 텐서를 지정한 장치로 옮긴다.
    (이미지는 리스트 컴프리헨션으로 간단히 옮길 수 있지만 target은 dict라 별도 처리)
    """
    return [{k: v.to(device) for k, v in t.items()} for t in targets]
