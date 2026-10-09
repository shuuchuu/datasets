# French Press 1914, Passages

64,610 passages of 100 to 250 words (median 118) cut from `french-press-1914`, the
OCR'd 1914 issues of *L'Humanité* (57,899 passages) and *Le Figaro* (6,711): a
corpus of reasonable units for search, topic modelling, extraction and question
answering labs.

## Files

- `passages.parquet`: one row per passage: `id` (`<newspaper>-<date>-<n>`),
  `newspaper`, `date`, `text`, `n_words`, `noise` (the share of its words that
  `wordfreq` doesn't know as French, at most 0.15).
- `build.py`: the script that built it from `../french-press-1914` (its docstring
  says how): OCR line-end hyphenations rejoined when the joined word is French, lines
  packed into passages ending at a sentence end, noisy passages and exact duplicates
  dropped. The OCR errors inside the passages are left as they are.

## Source

Derived from `french-press-1914`: BnF (Bibliothèque nationale de France), *Europeana
Newspapers French corpus (text format)*,
http://api.bnf.fr/europeana-newspapers-french-corpus-text-format

## License

Texts: public domain (Public Domain Mark,
https://creativecommons.org/publicdomain/mark/1.0/), like the source.
