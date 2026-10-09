# Drug Review Dataset (Drugs.com)

215,063 patient reviews of drugs from Drugs.com, with the drug's name, the patient's
condition, a 1–10 rating, the review's date and how many users found it useful.

## Files

- `drugsComTrain_raw.tsv`: 75% of the reviews.
- `drugsComTest_raw.tsv`: the other 25%.
- `drugsComTest_pain_fr.tsv`: a French machine translation (Google Translate, 2026-10)
  of the 926 reviews of `drugsComTest_raw.tsv` whose condition is `Pain` and rating 1
  or 10, with their HTML entities decoded. A monitoring lab swaps some of them in to
  simulate an ingestion bug that brings in a language the model wasn't trained on.

Tab-separated, columns: (unnamed id), `drugName`, `condition`, `review`, `rating`,
`date`, `usefulCount`; `drugsComTest_pain_fr.tsv` has `id` (the same id) and `review`.

## Source

- UCI Machine Learning Repository:
  https://archive.ics.uci.edu/dataset/462/drug+review+dataset+drugs+com
  (`drugsCom_raw.zip`, extracted)
- Gräßer, F. & Kallumadi, S. (2018). Drug Review Dataset (Drugs.com) [Dataset]. UCI
  Machine Learning Repository. https://doi.org/10.24432/C5SK5S
- Paper: Felix Gräßer, Surya Kallumadi, Hagen Malberg and Sebastian Zaunseder,
  "Aspect-Based Sentiment Analysis of Drug Reviews Applying Cross-Domain and Cross-Data
  Learning", *Proceedings of the 2018 International Conference on Digital Health*, ACM,
  121-125.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
