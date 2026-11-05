# frWac word2vec

French word embeddings: word2vec, CBOW, 200 dimensions, cutoff 100, trained on the frWac
corpus, with no lemmatization, no part-of-speech tagging and no phrases.

## Files

- `frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin.part-aa` and `.part-ab`: the model, in word2vec's binary format, cut in
  two because GitHub refuses a file over 100 MiB and compression leaves it at 117 MB.
  `cat frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin.part-* > frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin` puts it back together (SHA-256 `d51f3259d1f6fe12155a447623a82695c6d72916b1b61e150e2715c034b6c880`).

## Source

Jean-Philippe Fauconnier, *French Word Embeddings*, 2015:
https://fauconnier.github.io/, copied unchanged from
https://embeddings.net/embeddings/frWac_non_lem_no_postag_no_phrase_200_cbow_cut100.bin on 2026-11-05.

## License

CC BY 3.0, by Jean-Philippe Fauconnier (https://fauconnier.github.io/).
