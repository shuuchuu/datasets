# Nantes open data

Snapshots of Nantes Métropole open data, taken on 2026-09-29, to draw maps with them.

## Files

- `infos-velos.json`: availability of the bikes and stands of every Naolib (formerly
  Bicloo) bike-sharing station, as returned by the (legacy) API
  `https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=244400404_stations-velos-libre-service-nantes-metropole-disponibilites&q=&rows=1000`.
  - Source: *Disponibilité en temps réel des places et des vélos dans les stations vélos
    en libre-service Naolib de Nantes Métropole* (JCDecaux, now marked "[Ancien]"):
    https://data.nantesmetropole.fr/explore/dataset/244400404_stations-velos-libre-service-nantes-metropole-disponibilites/
- `zones.geojson`: outlines of the city of Nantes' polling areas.
  - Source: *Découpage géographique des bureaux de vote de la ville de Nantes* (Ville de
    Nantes):
    https://data.nantesmetropole.fr/explore/dataset/244400404_decoupage-geographique-bureaux-vote-nantes/
- `bureaux.geojson`: locations of Nantes Métropole's polling stations.
  - Source: *Lieux de vote de Nantes Métropole* (Nantes Métropole):
    https://data.nantesmetropole.fr/explore/dataset/244400404_lieux-vote-nantes-metropole/

## License

Licence Ouverte (Etalab), https://www.etalab.gouv.fr/licence-ouverte-open-licence, for
all three.
