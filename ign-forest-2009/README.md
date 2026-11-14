# IGN forest / non-forest, Lorraine 2009

Aerial photographs of the IGN (Institut national de l'information géographique et
forestière) taken in 2009 in Lorraine, with a forest / non-forest mask of each pixel,
for the image segmentation labs (`nn/cnn/image-segmentation-keras` and
`-lightning`).

20 areas of 5 km × 5 km, each cut into 9 × 9 = 81 tiles of 1024 × 1024 pixels (1 pixel
= 50 cm on the ground: a tile covers 512 m × 512 m). In the IGN's sense, a forest isn't
just trees: an area of more than 5,000 m², at least 20 m wide, where vegetation covers
at least 10 % of the ground, and which isn't farmed.

## Files

- `<split>/observations/<area>_<row>_<column>_observation_irc.jpg`: a tile in *color
  infrared* (CIR), three channels: near infrared, red and green. JPEG, quality 95.
- `<split>/annotations/<area>_<row>_<column>_0M50_pfnf_nch.png`: its mask, a 1-bit PNG
  of one channel, 1 for forest, 0 for non-forest (`imageio.v3.imread` or
  `numpy.asarray(PIL.Image.open(path))` read it as a boolean array).
- `train-files.csv`, `val-files.csv`, `test-files.csv`: the tiles of each split, one
  per row: `Observations` and `Annotations` (paths starting with `ign-forest-2009/`,
  from the directory where `ghsparse.sh` creates this folder), `latitude` and
  `longitude` (whatever their names, the area's Lambert-93 coordinates in kilometers,
  easting then northing), `ligne` and `colonne` (the tile's row and column in its
  area, 1 to 9), `coord` (the area).
- `nomenclature/`: the classes (`pfnf.csv`: 0 NonForet, 1 Foret) and their display
  colors (`clut_pfnf.txt`), as upstream.
- `convert.py`: the conversion from upstream; its docstring says how to run it again.

The splits are by area, so that neighboring tiles, too alike, never land in two splits:
`train` has 16 areas (1,296 tiles), `val` 2 (162 tiles), `test` 2 (160 tiles). 803 MB
in all.

## Changes from upstream

Converted on 2026-11-14 from https://github.com/mlambda/ign-FNF-2009 (8.1 GB of TIFF
files, about 4 GB to download), by `convert.py`:

- the images, 3-channel `uint8` TIFF, re-encoded as JPEG of quality 95 (Pillow's
  default 4:2:0 chroma subsampling): a mean absolute difference of 2.7 levels out of
  255 per pixel and channel;
- the masks, 2-channel one-hot TIFF, stored as their second channel (the class index),
  a 1-bit PNG: lossless;
- the validation tiles moved from `test/` to `val/`, the paths of the CSV files changed
  accordingly (folder, `.jpg`, `.png`), and the unnamed index column of `val-files.csv`
  and `test-files.csv` dropped;
- left out: two tiles of `test/` that no split lists (`915_6915_5_3`, `995_6850_9_8`),
  the per-tile class statistics (`*.xml`, `*.aux.xml`) and an empty
  `annotations_bdforet.csv`.

Upstream's README also describes a 6-class dataset (`dataset123_v1_512pix`) and a 2018
version of this one, which its repository doesn't hold.

## Source and license

Data obtained from the IGN (https://www.ign.fr/) on 2021-09-01, under the Licence
Ouverte / Open Licence of Etalab
(https://www.etalab.gouv.fr/licence-ouverte-open-licence). Source: IGN, 2009 aerial
photographs and forest / non-forest mask; converted by shuuchuu.
