# COCO val2017, open-licensed subset

943 photos of the COCO 2017 validation set, with their object annotations (boxes,
segmentations and classes, among COCO's 80), chosen because their photos are under
CC BY 2.0 or CC BY-SA 2.0, and their authors haven't moved them to a restrictive license
since. Used by the object detector pruning lab
(`mlops/modeling/compression/detector-pruning`), whose torchvision detectors were trained
on COCO train2017 and never saw these images.

## Files

- `images/<id>.jpg`: the 943 images, as COCO distributes them
  (`http://images.cocodataset.org/val2017/<id>.jpg`), unmodified; 156 MB.
- `annotations.json`: COCO's `instances_val2017.json` restricted to these images, in the
  same COCO format (`info`, `licenses`, `categories`, `images`, `annotations`):
  6,944 annotations, the crowd ones (`iscrowd: 1`) included, nothing else changed
  except `info.description`, and `licenses` reduced to the two used.
- `credits.csv`: one row per photo, to credit it:
  - `image_id`, `file_name`;
  - `license`, `license_url`: the photo's license as COCO recorded it when it collected
    the photo, the one this copy is distributed under;
  - `flickr_url`: the photo's file on Flickr, as COCO recorded it;
  - `flickr_page`, `author`, `author_url`: the photo's Flickr page and its author's name
    and page, looked up in 2026-10 from the photo id in `flickr_url` (Flickr's oEmbed
    endpoint, given the photo's `flic.kr` short URL; no API key): 763 photos. Empty for
    the 161 photos no longer on Flickr, and for 19 whose oEmbed answer gives none: COCO
    doesn't record authors;
  - `flickr_license_2026`: the license Flickr showed in 2026-10 (`photo removed` for a
    photo that is gone, empty for the 19 whose oEmbed answer gives none): CC BY 2.0 or
    CC BY-SA 2.0 for most, and for 4, a license as open (CC BY 4.0, Public Domain Mark,
    United States Government Work). This copy is distributed under the license of the
    `license` column.

## Selection

From `instances_val2017.json` (sha256
`e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f`, in
`annotations_trainval2017.zip`): the images whose `license` is 4 (CC BY 2.0) or 5
(CC BY-SA 2.0) and with at least one non-crowd annotation, 1,260 of the 5,000; then the
1,000 with the smallest ids, less the 57 whose author had changed their license on Flickr
by 2026-10, to `All Rights Reserved` (26) or to a NonCommercial or NoDerivs license
(31): a Creative Commons license can't be revoked for a copy already received under it,
but these authors no longer want their photos reused that way. The other licenses of
COCO's images are NonCommercial or NoDerivs (or, for 5 images, "no known copyright
restrictions").

| License | Images |
| --- | --- |
| CC BY 2.0 (`license` 4) | 631 |
| CC BY-SA 2.0 (`license` 5) | 312 |

## Source

- COCO: https://cocodataset.org (2017 Val images, 2017 Train/Val annotations)
- Tsung-Yi Lin, Michael Maire, Serge Belongie, Lubomir Bourdev, Ross Girshick, James
  Hays, Pietro Perona, Deva Ramanan, C. Lawrence Zitnick and Piotr Dollár, "Microsoft
  COCO: Common Objects in Context", ECCV 2014, https://arxiv.org/abs/1405.0312

## License

- Annotations: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), © COCO
  Consortium.
- Images: each photo's own license, CC BY 2.0
  (https://creativecommons.org/licenses/by/2.0/) or CC BY-SA 2.0
  (https://creativecommons.org/licenses/by-sa/2.0/), by its Flickr author:
  `credits.csv`.
