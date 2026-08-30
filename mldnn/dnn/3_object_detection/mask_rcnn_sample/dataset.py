"""
dataset.py
==========
[역할] 디스크의 이미지/마스크 파일을 읽어 Mask R-CNN이 요구하는 형식으로 바꿔 주는 모듈.

[Mask R-CNN이 요구하는 데이터 형식 — 가장 중요한 부분]
    __getitem__ 은 (image, target) 튜플을 반환해야 한다.

    image : FloatTensor [C, H, W], 값 범위 0.0 ~ 1.0

    target : dict, 아래 키를 가진다.
        boxes    : FloatTensor [N, 4]  - (x_min, y_min, x_max, y_max) 절대 픽셀 좌표
        labels   : Int64Tensor [N]     - 각 객체의 클래스 인덱스 (0은 배경이므로 1부터 시작)
        masks    : UInt8Tensor [N, H, W] - 객체별 이진 마스크 (0 또는 1)
        image_id : Int64Tensor [1]     - 평가 시 이미지를 식별하는 고유 번호
        area     : FloatTensor [N]     - 박스 면적 (COCO 평가에서 크기별 AP 계산에 사용)
        iscrowd  : UInt8Tensor [N]     - 1이면 "군중"으로 취급되어 평가에서 제외

    ※ N = 해당 이미지 안의 객체(instance) 개수. 이미지마다 다르다.

[이 데이터셋이 가정하는 디렉터리 구조 — PennFudan 형식]
    data_root/
        images/  0000.png, 0001.png, ...
        masks/   0000.png, 0001.png, ...

    마스크 PNG는 한 장에 모든 인스턴스가 담긴 "인스턴스 ID 맵"이다.
        픽셀값 0 = 배경
        픽셀값 1 = 첫 번째 객체
        픽셀값 2 = 두 번째 객체 ...
    즉, 색(정수값)이 곧 객체 ID다. 이 형식을 [N, H, W] 이진 마스크 스택으로
    풀어내는 것이 이 모듈의 핵심 작업이다.

[클래스 라벨은 어디서 오는가?]
    인스턴스 마스크만으로는 "이 객체가 원인지 사각형인지"를 알 수 없다.
    그래서 선택적으로 labels/xxxx.txt 파일을 읽어 클래스 인덱스를 가져온다.
    파일이 없으면 모든 객체를 클래스 1로 간주한다(단일 클래스 데이터셋).
"""

from __future__ import annotations

import os
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, Subset


class InstanceSegmentationDataset(Dataset):
    """인스턴스 ID 마스크 형식 데이터를 읽는 Dataset."""

    def __init__(
        self,
        root: str,
        transforms: Optional[Callable] = None,
        images_dirname: str = "images",
        masks_dirname: str = "masks",
        labels_dirname: str = "labels",
    ):
        """
        Args:
            root:       데이터 루트 디렉터리
            transforms: (image, target)을 함께 받는 증강 파이프라인 (transforms.py 참고)
        """
        self.root = root
        self.transforms = transforms
        self.images_dir = os.path.join(root, images_dirname)
        self.masks_dir = os.path.join(root, masks_dirname)
        self.labels_dir = os.path.join(root, labels_dirname)

        if not os.path.isdir(self.images_dir):
            raise FileNotFoundError(
                f"이미지 디렉터리를 찾을 수 없습니다: {self.images_dir}\n"
                f"먼저 `python make_dummy_dataset.py` 를 실행해 샘플 데이터를 만드세요."
            )

        # -------------------------------------------------------------
        # [단계 1] 파일 목록 수집
        #   - sorted()로 정렬하는 이유: OS마다 파일 나열 순서가 달라서
        #     정렬하지 않으면 image와 mask의 짝이 어긋날 수 있다.
        # -------------------------------------------------------------
        self.image_files = sorted(
            f for f in os.listdir(self.images_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        )
        if len(self.image_files) == 0:
            raise RuntimeError(f"{self.images_dir} 안에 이미지가 없습니다.")

    def __len__(self) -> int:
        """데이터셋의 전체 샘플 개수. DataLoader가 이 값을 기준으로 인덱싱한다."""
        return len(self.image_files)

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------
    def _load_labels(self, stem: str, num_instances: int) -> List[int]:
        """
        labels/<stem>.txt 에서 인스턴스별 클래스 인덱스를 읽는다.
        파일 형식: 한 줄에 하나의 정수, 마스크의 인스턴스 ID 순서(1, 2, 3...)와 일치.

        파일이 없으면 모든 객체를 클래스 1(첫 번째 전경 클래스)로 간주한다.
        """
        label_path = os.path.join(self.labels_dir, f"{stem}.txt")
        if not os.path.isfile(label_path):
            return [1] * num_instances

        with open(label_path, "r", encoding="utf-8") as f:
            labels = [int(line.strip()) for line in f if line.strip()]

        # 개수가 안 맞으면 데이터 오류이므로 즉시 알려 준다.
        # (조용히 넘어가면 학습이 이상하게 되는데 원인을 찾기 매우 어렵다)
        if len(labels) != num_instances:
            raise ValueError(
                f"{label_path}: 라벨 {len(labels)}개 vs 마스크 인스턴스 {num_instances}개 — 개수 불일치"
            )
        return labels

    # ------------------------------------------------------------------
    # 핵심: 한 샘플을 만들어 내는 함수
    # ------------------------------------------------------------------
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        image_file = self.image_files[idx]
        stem = os.path.splitext(image_file)[0]

        # -------------------------------------------------------------
        # [단계 1] 이미지 읽기
        #   convert("RGB")를 반드시 해 준다.
        #   흑백(L)이나 알파채널 포함(RGBA) 이미지가 섞여 있으면
        #   채널 수가 달라져 모델 입력에서 에러가 난다.
        # -------------------------------------------------------------
        img_path = os.path.join(self.images_dir, image_file)
        image = Image.open(img_path).convert("RGB")

        # -------------------------------------------------------------
        # [단계 2] 인스턴스 ID 마스크 읽기
        #   convert("L")로 읽어 [H, W] 단일 채널 정수 배열을 얻는다.
        #   여기서 각 픽셀값이 곧 인스턴스 ID다.
        # -------------------------------------------------------------
        mask_path = os.path.join(self.masks_dir, f"{stem}.png")
        mask = np.array(Image.open(mask_path).convert("L"))

        # -------------------------------------------------------------
        # [단계 3] ID 맵 -> 인스턴스별 이진 마스크 스택으로 분해
        #   np.unique로 등장하는 ID를 모으고 배경(0)을 제거한다.
        #   그 다음 브로드캐스팅 비교 한 번으로 [N, H, W] 불리언 스택을 만든다.
        #
        #   obj_ids            : [N]        -> [N, 1, 1] 로 reshape
        #   mask               : [H, W]
        #   mask == obj_ids[:, None, None]  ->  [N, H, W]  (각 객체별 True/False)
        # -------------------------------------------------------------
        obj_ids = np.unique(mask)
        obj_ids = obj_ids[obj_ids != 0]              # 배경(0) 제거
        num_objs = len(obj_ids)
        binary_masks = (mask == obj_ids[:, None, None]).astype(np.uint8)  # [N, H, W]

        # -------------------------------------------------------------
        # [단계 4] 각 마스크에서 bounding box 계산
        #   마스크가 True인 픽셀들의 최소/최대 x, y가 곧 박스가 된다.
        #
        #   [주의] torchvision은 x_max > x_min, y_max > y_min 인 "넓이가 0이 아닌"
        #         박스를 요구한다. 마스크가 1픽셀 두께면 x_max == x_min 이 되어
        #         학습 중 NaN이 발생한다. 따라서 아래에서 degenerate box를 걸러낸다.
        # -------------------------------------------------------------
        boxes: List[List[float]] = []
        keep_indices: List[int] = []

        for i in range(num_objs):
            ys, xs = np.where(binary_masks[i])
            if len(xs) == 0:      # 빈 마스크 방어 (리사이즈/크롭 과정에서 생길 수 있음)
                continue

            x_min, x_max = float(xs.min()), float(xs.max())
            y_min, y_max = float(ys.min()), float(ys.max())

            # 넓이가 0인 박스는 버린다.
            if x_max <= x_min or y_max <= y_min:
                continue

            boxes.append([x_min, y_min, x_max, y_max])
            keep_indices.append(i)

        binary_masks = binary_masks[keep_indices] if keep_indices else np.zeros(
            (0, *mask.shape), dtype=np.uint8
        )

        # -------------------------------------------------------------
        # [단계 5] 클래스 라벨 로드 (버려진 인스턴스는 함께 제거)
        # -------------------------------------------------------------
        all_labels = self._load_labels(stem, num_objs)
        labels = [all_labels[i] for i in keep_indices]

        # -------------------------------------------------------------
        # [단계 6] NumPy -> torch.Tensor 변환 (dtype이 매우 중요)
        #   boxes  : float32  (좌표는 실수 연산에 쓰임)
        #   labels : int64    (CrossEntropyLoss가 int64 타겟을 요구)
        #   masks  : uint8    (이진 마스크, 메모리 절약)
        #
        #   객체가 하나도 없는 이미지(negative sample)도 학습에 쓸 수 있다.
        #   이때는 N=0인 빈 텐서를 만들되 shape을 [0, 4] 처럼 정확히 맞춰 줘야 한다.
        # -------------------------------------------------------------
        if len(boxes) > 0:
            boxes_t = torch.as_tensor(boxes, dtype=torch.float32)
            labels_t = torch.as_tensor(labels, dtype=torch.int64)
            masks_t = torch.as_tensor(binary_masks, dtype=torch.uint8)
        else:
            boxes_t = torch.zeros((0, 4), dtype=torch.float32)
            labels_t = torch.zeros((0,), dtype=torch.int64)
            masks_t = torch.zeros((0, *mask.shape), dtype=torch.uint8)

        # 박스 면적: COCO 평가에서 small/medium/large AP를 나눌 때 사용한다.
        area = (boxes_t[:, 3] - boxes_t[:, 1]) * (boxes_t[:, 2] - boxes_t[:, 0])

        # iscrowd=1인 객체는 평가에서 무시된다. 여기서는 모두 0(일반 객체).
        iscrowd = torch.zeros((len(boxes_t),), dtype=torch.int64)

        target: Dict[str, torch.Tensor] = {
            "boxes": boxes_t,
            "labels": labels_t,
            "masks": masks_t,
            "image_id": torch.tensor([idx], dtype=torch.int64),
            "area": area,
            "iscrowd": iscrowd,
        }

        # -------------------------------------------------------------
        # [단계 7] 증강 적용
        #   image와 target을 함께 넘겨 박스/마스크도 같이 변형되게 한다.
        #   (transforms.py의 Compose 참고)
        # -------------------------------------------------------------
        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target


# ======================================================================
# 학습/검증 분할 헬퍼
# ======================================================================
def split_dataset(
    dataset: Dataset, val_ratio: float = 0.2, seed: int = 42
) -> Tuple[Subset, Subset]:
    """
    하나의 Dataset을 학습용/검증용 Subset 두 개로 나눈다.

    [주의] 학습셋과 검증셋은 서로 다른 transform을 써야 한다
           (검증셋에는 무작위 증강을 넣으면 안 됨).
           그런데 Subset은 원본 Dataset의 transform을 공유하므로,
           train.py에서는 **동일 경로에 대해 Dataset 객체를 두 번 만들고**
           같은 인덱스로 잘라내는 방식을 쓴다. 아래 build_dataloaders 참고.

    Returns:
        (train_indices, val_indices)를 적용한 Subset 두 개
    """
    num_samples = len(dataset)
    generator = torch.Generator().manual_seed(seed)   # 분할도 재현 가능하게
    indices = torch.randperm(num_samples, generator=generator).tolist()

    num_val = max(1, int(num_samples * val_ratio))
    val_indices = indices[:num_val]
    train_indices = indices[num_val:]

    return Subset(dataset, train_indices), Subset(dataset, val_indices)


def build_datasets(root: str, val_ratio: float, seed: int, build_transforms_fn: Callable):
    """
    학습/검증 Dataset을 만들어 반환한다.

    핵심 트릭: 같은 데이터 루트로 Dataset 인스턴스를 **두 개** 생성하되
              하나는 train transform, 다른 하나는 val transform을 갖게 한다.
              그리고 동일한 랜덤 인덱스로 각각 Subset을 만들어
              "서로 겹치지 않으면서 transform은 다른" 두 세트를 얻는다.
    """
    train_base = InstanceSegmentationDataset(root, transforms=build_transforms_fn(train=True))
    val_base = InstanceSegmentationDataset(root, transforms=build_transforms_fn(train=False))

    num_samples = len(train_base)
    generator = torch.Generator().manual_seed(seed)
    indices = torch.randperm(num_samples, generator=generator).tolist()

    num_val = max(1, int(num_samples * val_ratio))
    val_indices = indices[:num_val]
    train_indices = indices[num_val:]

    return Subset(train_base, train_indices), Subset(val_base, val_indices)
