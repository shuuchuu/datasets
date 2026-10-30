"""Rebuild `processed/` from `train.csv` and `test.csv`.

Mirrors, step by step, the solution of the data exploration lab of the
shuuchuu training slides (`labs/notebooks/ml/ames-data-exploration`), up to its
"Réassemblage" cell: the outlier removal and the log transform of the target,
which that lab applies afterwards, are not part of the output.

Usage (from any directory):

    python ames/make_processed.py

Needs pandas.
"""

from pathlib import Path

import pandas

here = Path(__file__).parent

train_df = pandas.read_csv(here / "train.csv", index_col="Id")
test_df = pandas.read_csv(here / "test.csv", index_col="Id")

train_X = train_df.drop(columns="SalePrice")
train_y = train_df["SalePrice"]
test_X = test_df
all_X = pandas.concat([train_X, test_X])

# Missing values. Fill values are computed on the train set only.
# Real values missing, numerical: the mean.
cols_mean = ["LotFrontage", "GarageYrBlt"]
all_X = all_X.fillna(train_X[cols_mean].mean())

# Real values missing, categorical: the mode.
cols_mode = [
  "MSZoning",
  "Electrical",
  "KitchenQual",
  "Exterior1st",
  "Exterior2nd",
  "SaleType",
  "Utilities",
]
all_X = all_X.fillna(train_X[cols_mode].mode().iloc[0])

# No basement, garage or veneer: 0.
cols_zero = [
  "GarageArea",
  "GarageCars",
  "BsmtFinSF1",
  "BsmtFinSF2",
  "BsmtFullBath",
  "BsmtHalfBath",
  "BsmtUnfSF",
  "MasVnrArea",
  "TotalBsmtSF",
]
all_X[cols_zero] = all_X[cols_zero].fillna(0)

# What data_description.txt dictates.
all_X["Functional"] = all_X["Functional"].fillna("Typ")

# Every other NA means "absent": a category of its own.
all_X = all_X.fillna("NA")
assert all_X.isnull().sum().sum() == 0

# MSSubClass is a category coded with numbers.
all_X[["MSSubClass"]] = all_X[["MSSubClass"]].astype(str)

# Ordinal variables: label encoding.
replace_mapping = dict(
  Alley=dict(NA=0, Grvl=1, Pave=2),
  BsmtExposure=dict(NA=0, No=1, Mn=2, Av=3, Gd=4),
  BsmtFinType1=dict(NA=0, Unf=1, LwQ=2, Rec=3, BLQ=4, ALQ=5, GLQ=6),
  BsmtFinType2=dict(NA=0, Unf=1, LwQ=2, Rec=3, BLQ=4, ALQ=5, GLQ=6),
  Functional=dict(Sal=1, Sev=2, Maj2=3, Maj1=4, Mod=5, Min2=6, Min1=7, Typ=8),
  LandSlope=dict(Sev=1, Mod=2, Gtl=3),
  LotShape=dict(IR3=1, IR2=2, IR1=3, Reg=4),
  PavedDrive=dict(NA=0, N=1, P=2, Y=3),
  Street=dict(Grvl=1, Pave=2),
  Utilities=dict(ELO=1, NoSeWa=2, NoSewr=3, AllPub=4),
  BsmtCond=dict(NA=0, Po=1, Fa=2, TA=3, Gd=4, Ex=5),
)
quality_columns = [
  "BsmtCond",
  "BsmtQual",
  "ExterCond",
  "ExterQual",
  "FireplaceQu",
  "GarageCond",
  "GarageQual",
  "HeatingQC",
  "KitchenQual",
  "PoolQC",
]
quality_mapping = dict(NA=0, Po=1, Fa=2, TA=3, Gd=4, Ex=5)
for quality_column in quality_columns:
  replace_mapping[quality_column] = quality_mapping

all_X = all_X.replace(replace_mapping)
ordinal_columns = list(replace_mapping.keys())
all_X[ordinal_columns] = all_X[ordinal_columns].astype(int)

# One-hot encoding of the nominal variables, both tables together so that they
# get the same columns.
all_X = pandas.get_dummies(all_X)

# Split again by Id.
train_X = all_X.loc[train_X.index]
test_X = all_X.loc[test_X.index]

out = here / "processed"
out.mkdir(exist_ok=True)
train_X.to_csv(out / "train_data.csv")
test_X.to_csv(out / "test_data.csv")
train_y.to_csv(out / "train_labels.csv")

print("train_data.csv:", train_X.shape)
print("test_data.csv:", test_X.shape)
print("train_labels.csv:", train_y.shape)
