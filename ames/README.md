# Ames Housing

Sale price and 79 explanatory variables for 2,919 residential homes sold in Ames, Iowa,
between 2006 and 2010, as split for Kaggle's *House Prices - Advanced Regression
Techniques* competition.

## Files

- `train.csv`: 1,460 houses, with their `SalePrice`.
- `test.csv`: 1,459 houses, without `SalePrice`.
- `data_description.txt`: description of every column and of its values.
- `sample_submission.csv`: example of the competition's submission format.
- `processed/`: `train.csv`/`test.csv` preprocessed for modeling (missing values filled
  in, categorical columns converted to numbers or one-hot encoded), as `train_data.csv`
  and `test_data.csv` (244 features each, `Id` as first column), the train set's
  `SalePrice` split out into `train_labels.csv`. Produced by `make_processed.py` (see
  below).
- `make_processed.py`: rebuilds `processed/` from `train.csv` and `test.csv`.

## Processed files

`python ames/make_processed.py` (pandas only) regenerates `processed/`. It follows, step
by step, the solution of the data exploration lab of the shuuchuu training slides
(`labs/notebooks/ml/ames-data-exploration`), up to its reassembly cell: fill values
(mean, mode, 0, `NA`) computed on the train set only, ordinal columns label encoded,
`MSSubClass` treated as a category, one-hot encoding of the train and test sets together.
The lab's later steps (removing the houses above 4,000 sq ft of living area, the log of
`SalePrice`) are not applied: `train_labels.csv` holds the raw prices. When the lab's
solution changes, change the script with it.

## Source

- Kaggle competition: https://www.kaggle.com/c/house-prices-advanced-regression-techniques
- Original data: Dean De Cock, "Ames, Iowa: Alternative to the Boston Housing Data as an
  End of Semester Regression Project", *Journal of Statistics Education*, 19(3), 2011,
  https://doi.org/10.1080/10691898.2011.11889627

## License

No explicit license. De Cock published the data for educational use; the files are
Kaggle's competition split, distributed under the competition's rules.
