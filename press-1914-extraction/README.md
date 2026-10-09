# French Press 1914, Entity Extraction

Named entities to extract from passages of `french-press-1914-passages`: the people,
places and organizations each passage names.

## Files

- `gold.jsonl`: 40 hand-annotated passages, one per line: `id` (the passage's id in
  `french-press-1914-passages`), `text`, `people`, `places`, `organizations`.
- `gold-records.py`: the annotations, and the script that writes `gold.jsonl`.

## Annotation guide

- Every entity the passage names, once, as it is written, OCR errors included (`Haras`
  for Havas), except words the OCR split across a line (`Fian- cette`: `Fiancette`).
- People without their title (`M.`, `Mme`, `sir`, `lord`, `le roi`).
- Places: countries, regions, towns, streets, named buildings and venues.
- Organizations: named institutions, assemblies, parties, unions, companies, news
  agencies and newspapers. Generic mentions (`le gouvernement`, `la police`) are not
  entities.
- Passages mixing several news items keep the entities of all of them.

Annotated by an LLM (Claude), each entity checked against its passage's text.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The passages themselves are
public domain.
