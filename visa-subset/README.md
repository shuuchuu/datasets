# VisA, two-category subset

Two categories of VisA (Visual Anomaly), Amazon's dataset of industrial images with
pixel-level defect masks, scaled down and laid out like MVTec AD, for the visual
anomaly detection labs (`nn/cnn/visual-anomaly-detection-keras` and
`-lightning`), which train on normal images only and locate defects at 256×256:

- `pcb4`: a battery charging circuit board (one object, defects such as missing,
  extra, misplaced or damaged components, burns, scratches, dirt);
- `chewinggum`: a piece of chewing gum on a textured background (a uniform surface,
  defects such as missing chunks or corners, spots, scratches, cracks).

They are the two categories of VisA whose defects are the largest (median mask area
0.93 % and 0.52 % of the image, against 0.05 % to 0.26 % for the others), so most stay
visible once scaled down.

## Files

For each category, in MVTec AD's layout:

- `<category>/train/good/`: 250 normal images, to train on;
- `<category>/test/good/`: normal test images (`pcb4`: 101, `chewinggum`: 50);
- `<category>/test/<defect>/`: anomalous test images (`pcb4`: 98, `chewinggum`: 94),
  one directory per defect, `combined` for an image with several;
- `<category>/ground_truth/<defect>/<name>_mask.png`: each anomalous image's defect
  mask, 0 (normal) or 255 (defect).

Images are JPEG, masks PNG, all 256 pixels high (`pcb4`: 315×256, `chewinggum`:
307×256). 23 MB in all. `prepare.py` rebuilds the subset from VisA's archive; its
docstring says how.

## Changes from VisA

- Only `pcb4` and `chewinggum`, from VisA's one-class split (`split_csv/1cls.csv`):
  250 of its normal training images (`pcb4`: 904, `chewinggum`: 453), evenly spaced
  in file name order, all of its normal test images, and its anomalous test images
  except those whose mask covers less than 0.1 % of the image (`pcb4`: 2,
  `chewinggum`: 6), invisible at 256×256.
- Scaled down from about 1,350×1,100 pixels to 256 on the shorter side (aspect ratio
  kept), and the images re-encoded as JPEG (quality 90).
- Masks binarized to 0 and 255 (VisA's are 0 and 1).
- Defect directories named after VisA's labels (`image_anno.csv`) in snake case, as
  MVTec AD does (VisA puts every anomalous image in one directory). Each file keeps
  the name of the VisA file it comes from (`Data/Images/Anomaly/008.JPG` is
  `test/burnt/008.jpg`).

## Source

- VisA: https://github.com/amazon-science/spot-diff, archive
  https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
- Yang Zou, Jongheon Jeong, Latha Pemula, Dongqing Zhang and Onkar Dabeer,
  "SPot-the-Difference Self-Supervised Pre-training for Anomaly Detection and
  Segmentation", ECCV 2022, https://arxiv.org/abs/2207.14315

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), © Amazon.com, Inc., as VisA
itself; this copy is modified as listed above.
