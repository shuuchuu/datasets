# OpenFlights airports and routes

The airports of OpenFlights' airport database (last changed in 2017) and the airline
routes between them, as of June 2014 (3,425 airport codes), for graph labs: a directed
graph whose vertices are the airports and whose edges are the routes.

## Files

- `airports.csv`: 7,698 airports, CSV with a header row: `airport_id` (OpenFlights' own
  identifier), `name`, `city`, `country`, `iata` (three-letter IATA code, empty for
  1,626 airports), `icao` (four-letter ICAO code), `latitude`, `longitude` (decimal
  degrees), `altitude` (feet), `utc_offset` (hours), `dst` (daylight saving time rule:
  `E` Europe, `A` US/Canada, `S` South America, `O` Australia, `Z` New Zealand, `N`
  none, `U` unknown; empty for 353), `tz` (Olson time zone), `type` (always `airport`), `source`
  (always `OurAirports`).
- `routes.csv`: 67,663 routes, CSV with a header row: `airline` (two-letter IATA or
  three-letter ICAO code), `airline_id`, `src` and `dst` (three-letter code of the
  source and destination airports), `src_id` and `dst_id` (their `airport_id`),
  `codeshare` (`Y` when the route is operated by another carrier), `stops` (0 for a
  direct flight), `equipment` (aircraft types, space-separated). A route is directional
  and given once per airline: an airline flying A to B and back has two rows; 14,597
  rows are codeshares. 406 sources and 416 destinations have no IATA code in
  `airports.csv` (airports missing from it, or listed there without their IATA code),
  729 routes in all.

## Source

- OpenFlights, https://openflights.org/data.php: `airports.dat` and `routes.dat` of
  https://github.com/jpatokal/openflights/tree/master/data (last changed 2017-02-02,
  downloaded 2026-11-20). The route data stopped being updated in June 2014: it is of
  historical value only.

The original files have no header and write a missing value as `\N`. The CSVs add the
header row (OpenFlights' field names, in snake case) and leave missing values empty;
nothing else is changed.

## License

Open Database License 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); the
individual contents under the Database Contents License
(https://opendatacommons.org/licenses/dbcl/1-0/). OpenFlights states that its airport
data, derived from OurAirports and DAFIF, and its route data, from Airline Route Mapper,
are in the public domain. Attribution: OpenFlights (https://openflights.org/).
