# datasets

Datasets used by shuuchuu's training labs (the Colab notebooks of
https://github.com/shuuchuu/labs), one per directory. Each directory's `README.md` gives
the dataset's content, source and license.

## Getting a dataset

Cloning this whole repository downloads every dataset. To get only one directory,
`ghsparse.sh` makes a sparse, partial clone of it, e.g. in Colab:

```
!wget -qO- https://github.com/shuuchuu/datasets/raw/refs/heads/main/ghsparse.sh | bash -s landscape
```

which creates `landscape/`. To get a single file:

```
!wget https://github.com/shuuchuu/datasets/raw/refs/heads/main/nginx-log/access-small.log
```

## Datasets

| Directory | Content | License |
| --- | --- | --- |
| `20newsgroups` | 20 Newsgroups Usenet posts (bydate split) | None stated |
| `ames` | Ames Housing sale prices (Kaggle split) | None stated (educational use) |
| `bike-sharing` | Capital Bikeshare hourly/daily rentals, 2011–2012 (UCI) | CC BY 4.0 |
| `classical-authors` | 9 English-language authors, 2 books each, by chapter | Public domain |
| `dpkg-logs` | dpkg logs of an Ubuntu machine | Own data |
| `drug-reviews` | Drugs.com patient reviews (UCI) | CC BY 4.0 |
| `dvf` | French real estate transactions 2014–2022, Parquet | Licence Ouverte 2.0 |
| `france-departements` | French départements and regions reference tables | PDDL / ODbL |
| `fraud-emails` | CLAIR "Nigerian" fraud e-mails | CC BY-SA 4.0 |
| `french-press-1914` | OCR'd 1914 issues of *L'Humanité* and *Le Figaro* (BnF) | Public domain |
| `french-press-1914-passages` | `french-press-1914` cut into 64,598 passages of 100–250 words | Public domain |
| `incident-response-log` | ServiceNow incident event log | CC0 |
| `landscape` | Intel natural scene images, 6 classes | © Original authors |
| `nantes-open-data` | Nantes bike stations and polling stations snapshots | Licence Ouverte |
| `nginx-log` | Online shop nginx access log | CC0 |
| `python-exercises` | Small files for Python course exercises | Own data / public domain |
| `titanic` | Titanic passengers (Kaggle split) | None stated |
| `titanic3` | Titanic passengers, full `titanic3` version (OpenML) | Public |
| `voltaire` | 10 works by Voltaire, in French | Public domain |
| `wikipedia-movie-plots` | Plots of 34,886 movies from Wikipedia | CC BY-SA 4.0 |
| `wine-quality` | Red Vinho Verde wine quality (UCI) | CC BY 4.0 |
