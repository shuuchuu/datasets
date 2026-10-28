"""Write the bike shop's till files: caisse.csv and tickets-2025.csv.

Standard library only, seeded: `python generate.py` writes the same bytes each time.
"""

import csv
import random
from pathlib import Path

HERE = Path(__file__).parent

# The four receipts of the till export, as a French-locale Excel writes them:
# `;` between fields, a decimal comma, cp1252, CRLF line ends.
CAISSE = [
    ("date", "ville", "code_postal", "produit", "montant"),
    ("05/01/2026", "Amiens", "80000", "vélo", "899,90"),
    ("12/01/2026", "Lille", "59000", "casque", "49,50"),
    ("20/01/2026", "Rennes", "35000", "casque", "-"),
    ("02/02/2026", "Nice", "06000", "casque", "39,00"),
]

# A million receipts of 2025 in the six cities of the shop.
VILLES = ["Lille", "Amiens", "Nice", "Marseille", "Nantes", "Rennes"]
N_TICKETS = 1_000_000


def write_caisse(path: Path) -> None:
    with path.open("w", encoding="cp1252", newline="") as f:
        csv.writer(f, delimiter=";", lineterminator="\r\n").writerows(CAISSE)


def write_tickets(path: Path) -> None:
    rng = random.Random(2025)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(("ville", "quantite", "montant"))
        for _ in range(N_TICKETS):
            quantite = rng.randint(1, 5)
            montant = round(quantite * rng.uniform(5, 120), 2)
            writer.writerow((rng.choice(VILLES), quantite, f"{montant:.2f}"))


if __name__ == "__main__":
    write_caisse(HERE / "caisse.csv")
    write_tickets(HERE / "tickets-2025.csv")
