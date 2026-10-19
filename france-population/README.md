# French population by département, 1975–2023 (INSEE)

INSEE's population estimates on January 1st of each year, by département, sex and broad
age group, as INSEE publishes them: an Excel workbook kept untouched, to practise reading
a real spreadsheet (one sheet per year, two header rows, total rows at the bottom).

## Files

- `estim-pop-dep-sexe-gca-1975-2023.xls`: the workbook (old Excel format, read by
  `pandas.read_excel` with `xlrd`). A first sheet `À savoir` holds INSEE's notes, then one
  sheet per year, `2023` down to `1975`. In each year's sheet:
  - rows 1–3: the title and the year;
  - rows 4–5: a two-level header, `Ensemble` / `Hommes` / `Femmes`, each split into
    `0 à 19 ans`, `20 à 39 ans`, `40 à 59 ans`, `60 à 74 ans`, `75 ans et plus` and
    `Total`;
  - then one row per département: its code (`01`… `2A`, `2B`… `976`, a string), its name,
    and the 18 counts;
  - then total rows (`France métropolitaine`, with a trailing space, then in the later
    years `DOM` and `France métropolitaine et DOM`) and the source line.

  Mayotte only appears from 2014 on. The figures of the latest years are provisional.

## Source

*Estimation de la population au 1ᵉʳ janvier*, INSEE, file *Estimation de population par
département, sexe et grande classe d'âge - Années 1975 à 2023*,
https://www.insee.fr/fr/statistiques/1893198 (file
https://www.insee.fr/fr/statistiques/fichier/1893198/estim-pop-dep-sexe-gca-1975-2023.xls,
downloaded 2026-10-19).

## License

Licence Ouverte / Open Licence 2.0 (Etalab,
https://www.etalab.gouv.fr/licence-ouverte-open-licence): reuse is free, citing INSEE as
the source.
