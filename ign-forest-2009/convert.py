"""Convert a clone of github.com/mlambda/ign-FNF-2009 into this folder.

Usage, from anywhere, with `numpy`, `pandas`, `pillow` and `tifffile` installed:

    git clone --depth 1 https://github.com/mlambda/ign-FNF-2009.git
    python ign-forest-2009/convert.py ign-FNF-2009

For each tile of the three splits (`train-files.csv`, `val-files.csv`,
`test-files.csv`), it writes:

- the color infrared image (a 3-channel `uint8` TIFF) as a JPEG of quality 95,
  `<split>/observations/<same base name>.jpg`;
- the forest mask, stored upstream as a 2-channel one-hot TIFF, as a 1-bit PNG
  of the one-hot's second channel (1 = forest, 0 = non-forest), lossless,
  `<split>/annotations/<same base name>.png`.

`<split>` is the CSV's split: upstream keeps the validation tiles in `test/`.
It then writes the three CSV files with the new paths and extensions, without
the unnamed index column two of them have, every other column unchanged, and
copies `nomenclature/`. It checks each tile's shape, that each mask pixel is
one-hot, and prints the clone's tiles that no split lists (two in `test/`),
which it leaves out, as it does the per-tile statistics files (`*.xml`).
"""

import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path, PurePosixPath

import numpy
import pandas
from PIL import Image
from tifffile import imread

SOURCE_PREFIX = "ign-FNF-2009/"
TARGET_PREFIX = "ign-forest-2009"
SPLITS = ("train", "val", "test")
TILE_SIZE = 1024


def new_path(path: str, split: str, suffix: str) -> str:
    """A tile's path here, from its upstream path and its split.

    E.g. `ign-FNF-2009/test/annotations/x.tif`, of the `val` split:
    `ign-forest-2009/val/annotations/x.png`.
    """
    parts = PurePosixPath(path).parts
    assert len(parts) == 4 and parts[0] == SOURCE_PREFIX[:-1], path
    _, _, kind, name = parts
    assert name.endswith(".tif"), path
    return str(PurePosixPath(TARGET_PREFIX, split, kind, name).with_suffix(suffix))


def convert_tile(
    source: Path,
    target: Path,
    observation: str,
    image_to: str,
    annotation: str,
    mask_to: str,
) -> None:
    image = imread(source / observation.removeprefix(SOURCE_PREFIX))
    assert image.shape == (TILE_SIZE, TILE_SIZE, 3), (observation, image.shape)
    assert image.dtype == numpy.uint8, (observation, image.dtype)
    one_hot = imread(source / annotation.removeprefix(SOURCE_PREFIX))
    assert one_hot.shape == (TILE_SIZE, TILE_SIZE, 2), (annotation, one_hot.shape)
    assert (one_hot.sum(axis=-1) == 1).all(), annotation
    image_path = target / PurePosixPath(image_to).relative_to(TARGET_PREFIX)
    mask_path = target / PurePosixPath(mask_to).relative_to(TARGET_PREFIX)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    mask_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(image_path, quality=95)
    Image.fromarray(one_hot[..., 1].astype(bool)).save(mask_path, optimize=True)


def main(source: Path, target: Path) -> None:
    listed = set()
    with ProcessPoolExecutor() as executor:
        for split in SPLITS:
            df = pandas.read_csv(source / f"{split}-files.csv", dtype=str)
            df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed:")])
            images = [new_path(p, split, ".jpg") for p in df.Observations]
            masks = [new_path(p, split, ".png") for p in df.Annotations]
            futures = [
                executor.submit(convert_tile, source, target, *paths)
                for paths in zip(
                    df.Observations, images, df.Annotations, masks, strict=True
                )
            ]
            for future in futures:
                future.result()
            listed.update(p.removeprefix(SOURCE_PREFIX) for p in df.Observations)
            df["Observations"] = images
            df["Annotations"] = masks
            df.to_csv(target / f"{split}-files.csv", index=False)
            print(f"{split}: {len(df)} tiles")
    tiles = {str(p.relative_to(source)) for p in source.rglob("observations/*_irc.tif")}
    assert listed <= tiles, sorted(listed - tiles)[:10]
    print("Tiles in no split, left out:", *sorted(tiles - listed), sep="\n  ")
    shutil.copytree(
        source / "nomenclature", target / "nomenclature", dirs_exist_ok=True
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(__file__).resolve().parent)
