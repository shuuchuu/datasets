# DVF (Demandes de valeurs foncières), linearized

French real estate transactions from 2014 to 2022, geolocated, one row per transaction.

## Files

- `dvf-linearized-2014-2022.parquet/`: a Parquet dataset partitioned by year
  (`annee_mutation=<year>/`). Read the whole directory with
  `pandas.read_parquet("dvf/dvf-linearized-2014-2022.parquet")` or
  `spark.read.parquet(...)`.

## Source

- Original data: *Demandes de valeurs foncières géolocalisées*, Etalab,
  https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/
- Cleaned, linearized version: https://github.com/NyxAether/DVF
- Converted to a single Parquet dataset, with compact types, for shuuchuu's courses:

  ```python
  from bz2 import open as bz2_open
  from pickle import load as pickle_load

  from pandas import DataFrame, concat


  def load(year: int) -> DataFrame:
      with bz2_open(f"clean_data/{year}_cleaned.pkl.bz2", mode="rb") as fh:
          df = pickle_load(fh)
          if year not in (2014, 2015):
              df.set_index("id_mutation", inplace=True)
          return df


  df = concat(map(load, range(2014, 2023)))

  surface_columns = (c for c in df.columns if c.startswith("surface_"))
  nombre_columns = (c for c in df.columns if c.startswith("nombre_"))

  df.code_departement = df.code_departement.astype("str")

  df = df.astype(
      {
          **{c: "uint16" for c in nombre_columns},
          **{c: "float32" for c in surface_columns},
          **dict(
              code_postal="uint32",
              code_departement="category",
              nature_mutation="category",
              adresse_suffixe="category",
              nature_culture="category",
              nature_culture_speciale="category",
              jour_mutation="uint8",
              mois_mutation="uint8",
              annee_mutation="uint16",
              adresse_numero="uint16",
          ),
      }
  )
  df.replace({"<EMPTY>": None}, inplace=True)
  df.to_parquet(
      "dvf-linearized-2014-2022.parquet",
      engine="pyarrow",
  ```

## License

Licence Ouverte 2.0 (Etalab), https://www.etalab.gouv.fr/licence-ouverte-open-licence
