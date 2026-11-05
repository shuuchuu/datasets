# French Hunspell dictionary

The "Classique" French spelling dictionary of Grammalecte (version 7.5), for Hunspell: the
known-word test of the press corpus tokenization lab.

## Files

- `fr.aff`, `fr.dic`: the affix file and the dictionary, unchanged, only renamed from
  `index.aff` and `index.dic` so that `Hunspell("fr", hunspell_data_dir="dictionary-fr")`
  finds them (SHA-256 `05a735d34c912e4e381ff08ee7c747923ccf5cf9dca81d8467982fa1ca51c2b7` and `984e933237bc1224a48f42828233be9b03228260ef67aa8e2bdddcd03a26230d`).
- `LICENSE`: the dictionary's own notice, unchanged (`license` in the package).
- `MPL-2.0.txt`: the license's text, from https://www.mozilla.org/media/MPL/2.0/index.txt.

## Source

Olivier R. and the contributors `LICENSE` names, https://grammalecte.net/, as packaged by
Titus Wormer in the npm package `dictionary-fr` 3.0.0
(https://github.com/wooorm/dictionaries/tree/main/dictionaries/fr), copied on 2026-11-05.

## License

Mozilla Public License 2.0. These files are its Source Code Form: they are the same as
the package's, which is where to get them from too.
