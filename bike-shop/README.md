# Bike shop till files

Made-up till files of the fictional bike shop of shuuchuu's pandas course (Lille,
Amiens, Nice, Marseille, Nantes and Rennes), for the course notes' chapters on reading
files and on column types.

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

## Source

Written for shuuchuu's pandas course by Shuuchuu; the receipts are invented.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
