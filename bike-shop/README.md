# Bike shop till files and rentals

Made-up data of the fictional bike shop of shuuchuu's pandas course (Lille, Amiens,
Nice, Marseille, Nantes and Rennes), for the course notes' pandas chapters: reading
files, column types, dates and time series.

## Files

- `caisse.csv`: the till export, four receipts as Excel set to French writes them:
  `;` between fields, a decimal comma, Windows-1252 (`cp1252`), CRLF line ends. Columns
  `date` (`DD/MM/YYYY`), `ville`, `code_postal` (`06000`, with its leading zero),
  `produit`, `montant` (`-` for a missing amount).
- `tickets-2025.csv`: a million receipts of 2025, UTF-8, `,` between fields. Columns
  `ville` (one of the six cities, drawn at random), `quantite` (1 to 5), `montant`
  (euros, two decimals).
- `generate.py`: writes both files (`python generate.py`, standard library only,
  seeded).
- `velos.csv`: the shop's daily bike rentals, 2025-01-01 to 2026-06-30, UTF-8. Columns
  `date` (ISO), `locations` (rentals that day), `temperature` (°C, one decimal).
  Synthetic: a seasonal temperature, fewer rentals at weekends and on rainy days, drawn
  with NumPy from a fixed seed by the figure code of shuuchuu's pandas slides
  (`bike_rentals()`), whose plots show the same data.

## Source

Written for shuuchuu's pandas course by Shuuchuu; the receipts and rentals are invented.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
