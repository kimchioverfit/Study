"""
make_dummy_dataset.py
=====================
[역할] 학습 코드를 곧바로 돌려 볼 수 있도록 **합성(synthetic) 데이터셋**을 생성한다.

[왜 필요한가?]
    Mask R-CNN 학습 코드의 구조를 익히는 것이 목적인데, 실제 데이터셋(COCO 등)을
    내려받으면 수십 GB를 기다려야 한다. 여기서는 도형(원/사각형)을 무작위로 그려
    "이미지 + 인스턴스 마스크 + 클래스 라벨" 세트를 즉석에서 만든다.
    데이터가 아주 단순하므로 몇 epoch만 돌려도 loss가 눈에 띄게 떨어지는 것을
    확인할 수 있어 학습 파이프라인이 제대로 동작하는지 검증하기 좋다.

[생성되는 구조]
    data/
      images/ 0000.png ...      RGB 이미지
      masks/  0000.png ...      인스턴스 ID 맵 (0=배경, 1,2,3...=각 객체)
      labels/ 0000.txt ...      각 줄이 인스턴스 1개의 클래스 인덱스

[클래스 정의]
    1 = circle (원)
    2 = rectangle (사각형)
    (0은 언제나 배경이므로 사용하지 않는다)

실행:
    python make_dummy_dataset.py --num-images 60 --out data
"""

from __future__ import annotations

import argparse
import os
import random

import numpy as np
from PIL import Image, ImageDraw

CLASS_CIRCLE = 1
CLASS_RECTANGLE = 2


def _random_color(rng: random.Random) -> tuple:
    """너무 어둡지 않은 무작위 RGB 색을 만든다."""
    return (rng.randint(60, 255), rng.randint(60, 255), rng.randint(60, 255))


def generate_one_sample(
    width: int,
    height: int,
    max_objects: int,
    rng: random.Random,
):
    """
    이미지 한 장과 그에 대응하는 인스턴스 마스크/라벨을 생성한다.

    Returns:
        image  : PIL.Image (RGB)
        mask   : PIL.Image (L 모드, 픽셀값 = 인스턴스 ID)
        labels : List[int] 인스턴스 순서대로의 클래스 인덱스
    """
    # ------------------------------------------------------------------
    # [단계 1] 배경 만들기 — 옅은 무작위 단색 + 약간의 노이즈
    #   완전 단색이면 모델이 너무 쉽게 학습해 버려서 약간의 잡음을 넣는다.
    # ------------------------------------------------------------------
    bg_value = rng.randint(200, 240)
    background = np.full((height, width, 3), bg_value, dtype=np.uint8)
    noise = np.random.randint(-12, 12, size=background.shape, dtype=np.int16)
    background = np.clip(background.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    image = Image.fromarray(background)
    image_draw = ImageDraw.Draw(image)

    # ------------------------------------------------------------------
    # [단계 2] 인스턴스 ID 마스크 캔버스 준비
    #   모드 "L" = 8비트 그레이스케일. 픽셀값을 인스턴스 ID로 쓴다.
    #   0으로 채워 두면 전부 배경이다.
    # ------------------------------------------------------------------
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)

    labels: list[int] = []
    num_objects = rng.randint(1, max_objects)

    # ------------------------------------------------------------------
    # [단계 3] 객체를 하나씩 그린다.
    #   중요한 점: **이미지와 마스크에 동일한 위치/모양으로 그린다.**
    #   이미지에는 색으로, 마스크에는 인스턴스 ID(1, 2, 3...)로 그리는 것이 차이.
    # ------------------------------------------------------------------
    for instance_id in range(1, num_objects + 1):
        shape_type = rng.choice([CLASS_CIRCLE, CLASS_RECTANGLE])
        color = _random_color(rng)

        size = rng.randint(30, min(width, height) // 3)
        x0 = rng.randint(0, width - size - 1)
        y0 = rng.randint(0, height - size - 1)
        box = [x0, y0, x0 + size, y0 + size]

        if shape_type == CLASS_CIRCLE:
            image_draw.ellipse(box, fill=color)
            mask_draw.ellipse(box, fill=instance_id)   # 마스크에는 ID를 채운다
        else:
            image_draw.rectangle(box, fill=color)
            mask_draw.rectangle(box, fill=instance_id)

        labels.append(shape_type)

    # ------------------------------------------------------------------
    # [단계 4] 가려짐(occlusion) 처리
    #   나중에 그린 도형이 앞의 도형을 덮으면, 마스크에서도 뒤 도형의 ID가
    #   덮어써진다(그리기 순서가 곧 깊이 순서). 이때 완전히 가려져
    #   마스크에서 사라진 인스턴스가 생길 수 있다.
    #   dataset.py는 np.unique로 실제 존재하는 ID만 읽으므로 마스크는 문제없지만,
    #   labels 파일과 개수가 어긋나면 안 되므로 여기서 정리해 준다.
    # ------------------------------------------------------------------
    mask_np = np.array(mask)
    surviving_ids = sorted(int(i) for i in np.unique(mask_np) if i != 0)

    # 살아남은 ID를 1부터 다시 촘촘하게 번호를 매긴다 (1, 2, 3... 연속되도록).
    remapped = np.zeros_like(mask_np)
    final_labels = []
    for new_id, old_id in enumerate(surviving_ids, start=1):
        remapped[mask_np == old_id] = new_id
        final_labels.append(labels[old_id - 1])

    return image, Image.fromarray(remapped, mode="L"), final_labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Mask R-CNN 학습용 합성 데이터셋 생성기")
    parser.add_argument("--out", type=str, default="data", help="출력 디렉터리")
    parser.add_argument("--num-images", type=int, default=60, help="생성할 이미지 수")
    parser.add_argument("--width", type=int, default=320)
    parser.add_argument("--height", type=int, default=320)
    parser.add_argument("--max-objects", type=int, default=4, help="이미지당 최대 객체 수")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    np.random.seed(args.seed)

    images_dir = os.path.join(args.out, "images")
    masks_dir = os.path.join(args.out, "masks")
    labels_dir = os.path.join(args.out, "labels")
    for d in (images_dir, masks_dir, labels_dir):
        os.makedirs(d, exist_ok=True)

    for i in range(args.num_images):
        image, mask, labels = generate_one_sample(
            args.width, args.height, args.max_objects, rng
        )
        stem = f"{i:04d}"
        image.save(os.path.join(images_dir, f"{stem}.png"))
        mask.save(os.path.join(masks_dir, f"{stem}.png"))
        with open(os.path.join(labels_dir, f"{stem}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(str(v) for v in labels))

    print(f"[완료] {args.num_images}개 샘플을 '{args.out}' 에 생성했습니다.")
    print(f"  - 이미지: {images_dir}")
    print(f"  - 마스크: {masks_dir}  (픽셀값 = 인스턴스 ID)")
    print(f"  - 라벨  : {labels_dir}  (1=circle, 2=rectangle)")


if __name__ == "__main__":
    main()
