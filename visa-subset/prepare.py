"""Build the subset from VisA's archive (run from this directory).

    tar xf VisA_20220922.tar -C <VisA dir>
    uv run --no-project --with numpy --with pillow python prepare.py <VisA dir>

The archive is https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
(1.9 GB). For each of `CATEGORIES`, it writes `<category>/` in MVTec AD's layout, from
VisA's one-class split (`split_csv/1cls.csv`):

- `train/good/`: `N_TRAIN` of the split's normal training images, evenly spaced in
  file name order;
- `test/good/`: every normal test image of the split;
- `test/<defect>/` and `ground_truth/<defect>/<name>_mask.png`: every anomalous test
  image of the split whose mask covers at least `MIN_MASK_FRACTION` of the image (the
  others are invisible at the 256×256 the labs use), with its mask (0 or 255).
  `<defect>` is VisA's label (`image_anno.csv`) in snake case, `combined` for an image
  with several.

Images are scaled down to `SHORT_SIDE` pixels on their shorter side (aspect ratio
kept), as JPEG (quality `JPEG_QUALITY`); masks to the same size, as PNG. Each file
keeps the name of the VisA file it comes from (`Data/Images/Normal/0836.JPG` becomes
`train/good/0836.jpg`).
"""

import csv
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

CATEGORIES = ("pcb4", "chewinggum")
N_TRAIN = 250
MIN_MASK_FRACTION = 0.001
SHORT_SIDE = 256
JPEG_QUALITY = 90

source = Path(sys.argv[1])
out = Path(__file__).resolve().parent
split = list(csv.DictReader((source / "split_csv" / "1cls.csv").open(encoding="utf-8")))


def scaled_size(size: tuple[int, int]) -> tuple[int, int]:
    width, height = size
    ratio = SHORT_SIDE / min(width, height)
    return round(width * ratio), round(height * ratio)


def save_image(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image = image.convert("RGB")
        image.resize(scaled_size(image.size), Image.Resampling.LANCZOS).save(
            dest, quality=JPEG_QUALITY
        )


def save_mask(mask: np.ndarray, size: tuple[int, int], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8))
    image.resize(scaled_size(size), Image.Resampling.NEAREST).save(dest)


def defect(labels: str) -> str:
    names = [name.strip() for name in labels.split(",")]
    if len(names) > 1:
        return "combined"
    return re.sub(r"[^a-z0-9]+", "_", names[0].lower()).strip("_")


for category in CATEGORIES:
    shutil.rmtree(out / category, ignore_errors=True)
    rows = [row for row in split if row["object"] == category]
    with (source / category / "image_anno.csv").open(encoding="utf-8") as f:
        labels = {row["image"]: row["label"] for row in csv.DictReader(f)}

    train = sorted(
        r["image"] for r in rows if r["split"] == "train" and r["label"] == "normal"
    )
    for i in range(N_TRAIN):
        image = train[i * len(train) // N_TRAIN]
        save_image(source / image, out / category / "train" / "good" / f"{Path(image).stem}.jpg")

    kept = dropped = 0
    for row in sorted(rows, key=lambda r: r["image"]):
        if row["split"] != "test":
            continue
        stem = Path(row["image"]).stem
        if row["label"] == "normal":
            save_image(source / row["image"], out / category / "test" / "good" / f"{stem}.jpg")
            continue
        with Image.open(source / row["mask"]) as image:
            size, mask = image.size, np.array(image.convert("L")) > 0
        if mask.mean() < MIN_MASK_FRACTION:
            dropped += 1
            continue
        kept += 1
        name = defect(labels[row["image"]])
        save_image(source / row["image"], out / category / "test" / name / f"{stem}.jpg")
        save_mask(mask, size, out / category / "ground_truth" / name / f"{stem}_mask.png")
    print(f"{category}: {N_TRAIN} training images, {kept} anomalies kept, {dropped} dropped")
