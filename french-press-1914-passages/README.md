# French Press 1914, Passages

64,598 passages of 100 to 250 words (median 118) cut from `french-press-1914`, the
OCR'd 1914 issues of *L'Humanité* (57,875 passages) and *Le Figaro* (6,723): a
corpus of reasonable units for search, topic modelling, extraction and question
answering labs.

## Files

- `passages.parquet`: one row per passage: `id` (`<newspaper>-<date>-<n>`),
  `newspaper`, `date`, `text`, `n_words`, `noise` (the share of its words that
  `wordfreq` doesn't know as French, at most 0.15).
- `build.py`: the script that built it from `../french-press-1914` (its docstring
  says how): OCR line-end hyphenations and spaced splits ("gou vernement") rejoined when the
  joined word is French, lines
  packed into passages ending at a sentence end, noisy passages and exact duplicates
  dropped. The OCR errors inside the passages are left as they are.
- `embeddings-512.npy`: the passages' embeddings, in `passages.parquet`'s order, a
  float16 array of shape (64598, 512): `Qwen/Qwen3-Embedding-0.6B`
  (sentence-transformers' `encode_document`, `max_seq_length` 512, in float16 on a
  GPU), truncated to their first 512 dimensions (the model is trained Matryoshka-style)
  and normalized to unit length. Encode queries with the same model and
  `truncate_dim=512` (`encode_query`), and normalize them.

## Source

Derived from `french-press-1914`: BnF (Bibliothèque nationale de France), *Europeana
Newspapers French corpus (text format)*,
http://api.bnf.fr/europeana-newspapers-french-corpus-text-format

## License

Texts: public domain (Public Domain Mark,
https://creativecommons.org/publicdomain/mark/1.0/), like the source.
