# MASSIVE Intents (French and English)

Amazon's MASSIVE dataset, intent classification only, French (`fr-FR`) and English
(`en-US`): short requests to a voice assistant ("réveille-moi à neuf heures", "wake me
up at nine am"), each with one of 60 intents. The two languages are translations of
each other, with the same `id`.

## Files

- `<fr|en>-<train|validation|test>.parquet`: `id`, `text`, `label` (11,514 / 2,033 /
  2,974 requests per language), the original splits.
- `intents.csv`: each intent's one-line description, in French and English (written for
  the labs, not part of MASSIVE).
- `lab-results/predictions-<fr|en>.csv` and `lab-results/timings-<fr|en>.csv`: the
  results of the encoder classification lab (one Colab T4 run per language), which the
  LLM classification lab compares with: each method's prediction for every test request
  (`id`, `label`, one column per method), and each method's training time (`train_s`) and
  prediction time per request (`ms_per_text`).

## Source

FitzGerald et al., *MASSIVE: A 1M-Example Multilingual Natural Language Understanding
Dataset with 51 Typologically-Diverse Languages* (2022),
https://github.com/alexa/massive, through the Parquet files of
https://huggingface.co/datasets/mteb/amazon_massive_intent

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Amazon.com, Inc.
`intents.csv`: CC BY 4.0 too.
