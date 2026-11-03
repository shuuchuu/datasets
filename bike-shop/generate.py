"""Write the bike shop's files: caisse.csv, tickets-2025.csv and their en/ versions.

Standard library only, seeded: `python generate.py` writes the same bytes each time.
The en/ files hold the same rows under English column names, for the English course
notes: en/till.csv, en/tickets-2025.csv, and en/bikes.csv, copied from velos.csv
(which the slides' figure code writes, not this script).
"""

import csv
import random
from pathlib import Path

HERE = Path(__file__).parent
EN = HERE / "en"

# The four receipts of the till export, as a French-locale Excel writes them:
# `;` between fields, a decimal comma, cp1252, CRLF line ends. The English version
# keeps the format and the values (the English slides show `vélo`): only the header
# changes.
CAISSE_HEADER = ("date", "ville", "code_postal", "produit", "montant")
TILL_HEADER = ("date", "city", "postcode", "product", "amount")
CAISSE = [
    ("05/01/2026", "Amiens", "80000", "vélo", "899,90"),
    ("12/01/2026", "Lille", "59000", "casque", "49,50"),
    ("20/01/2026", "Rennes", "35000", "casque", "-"),
    ("02/02/2026", "Nice", "06000", "casque", "39,00"),
]

# A million receipts of 2025 in the six cities of the shop.
TICKETS_HEADER = ("ville", "quantite", "montant")
TICKETS_HEADER_EN = ("city", "quantity", "amount")
VILLES = ["Lille", "Amiens", "Nice", "Marseille", "Nantes", "Rennes"]
N_TICKETS = 1_000_000

VELOS_HEADER = "date,locations,temperature"
BIKES_HEADER = "date,rentals,temperature"


def write_caisse(path: Path, header: tuple[str, ...]) -> None:
    with path.open("w", encoding="cp1252", newline="") as f:
        csv.writer(f, delimiter=";", lineterminator="\r\n").writerows([header, *CAISSE])


def write_tickets(path: Path, header: tuple[str, ...]) -> None:
    rng = random.Random(2025)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        for _ in range(N_TICKETS):
            quantite = rng.randint(1, 5)
            montant = round(quantite * rng.uniform(5, 120), 2)
            writer.writerow((rng.choice(VILLES), quantite, f"{montant:.2f}"))


def write_bikes(path: Path) -> None:
    header, rows = (HERE / "velos.csv").read_text(encoding="utf-8").split("\n", 1)
    if header != VELOS_HEADER:
        raise ValueError(f"velos.csv: unexpected header {header!r}")
    path.write_text(f"{BIKES_HEADER}\n{rows}", encoding="utf-8", newline="")


if __name__ == "__main__":
    EN.mkdir(exist_ok=True)
    write_caisse(HERE / "caisse.csv", CAISSE_HEADER)
    write_caisse(EN / "till.csv", TILL_HEADER)
    write_tickets(HERE / "tickets-2025.csv", TICKETS_HEADER)
    write_tickets(EN / "tickets-2025.csv", TICKETS_HEADER_EN)
    write_bikes(EN / "bikes.csv")
