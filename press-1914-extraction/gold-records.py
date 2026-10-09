"""The hand-annotated records of gold.jsonl (python gold-records.py writes it)."""

import json
from pathlib import Path

import pandas as pd

R = {
    "l_humanite-1914-06-20-100": (["Galil bey", "Wilson"], ["Asie-Mineure", "Athènes", "Turquie", "Niagara-Falls", "Washington", "Etats-Unis", "Mexique"], ["Porte"]),
    "l_humanite-1914-06-20-110": ([], ["Hill Crest", "Ernie", "Colombie anglaise", "Bruxelles", "Anvers"], ["Parlement"]),
    "l_humanite-1914-06-22-099": (["Jouhaux", "Barrio", "Machado"], ["Madrid", "Théâtre Espagnol", "Asturies"], ["Union générale des travailleurs", "Maison du peuple de Madrid", "Syndicat des mineurs des Asturies", "C. G. T."]),
    "l_humanite-1914-06-22-192": ([], [], ["Congrès olympique"]),
    "l_humanite-1914-06-26-092": ([], ["Saint-Pétersbourg"], ["Douma", "Conseil de l'Empire", "Sénat", "Havas"]),
    "l_humanite-1914-06-27-192": (["Lapize", "Petit-Breton"], ["Parc des Princes"], []),
    "l_humanite-1914-06-27-098": (["Stassof"], [], []),
    "l_humanite-1914-06-30-091": ([], ["Bosnie-Herzégovine", "Budapest", "Sarajevo"], ["Diète", "Havas"]),
    "l_humanite-1914-07-02-175": (["Ginisty", "Le Bargy", "Regnault", "Coquelin"], [], ["Comédie-Française"]),
    "l_humanite-1914-07-05-039": (["Sellier", "Fiancette"], ["Hôtel de Ville"], ["Parlement", "groupe socialiste"]),
    "l_humanite-1914-07-09-032": (["Augereau", "Roger Darlavoid"], ["rue de la Mairie", "Ivry"], []),
    "l_humanite-1914-07-09-116": (["Pierre", "Alexandre"], ["Bosnie", "Bosnie-Herzégovine", "Belgrade"], ["Agence des Balkans"]),
    "l_humanite-1914-07-09-033": (["Jouard", "Darlavoid", "Augereau"], [], ["Sénat"]),
    "l_humanite-1914-07-10-070": (["Pierre Castaing", "Oscar Mayzou", "Saint-Martin"], ["Toulouse"], []),
    "l_humanite-1914-07-11-022": (["Paul Morel", "Puech"], [], []),
    "l_humanite-1914-07-17-031": (["Calmette", "Hartmann", "Cunéo", "Reymond", "Cailîaux"], ["rue Drouot", "Neuilly"], ["Figaro"]),
    "l_humanite-1914-07-17-241": (["Jaurès", "Ferdinand Faure"], [], ["Conseil national", "Parlement", "Commission des conflits"]),
    "l_humanite-1914-07-17-152": ([], ["Paris", "Bois de Boulogne", "Bois de Vincennes"], ["Société des glacières", "Ville de Paris"]),
    "l_humanite-1914-07-22-007": (["Clemenceau"], [], []),
    "l_humanite-1914-07-23-147": (["Francis Lucas", "Laure"], ["rue des Filles-du-Calvaire"], []),
    "l_humanite-1914-07-25-120": ([], ["Serbie", "Europe", "Autriche"], ["La Libre Parole", "La Lanterne"]),
    "l_humanite-1914-07-26-113": ([], ["Roumanie"], ["La Politique"]),
    "l_humanite-1914-07-26-109": (["Cambon", "Edward Grey", "Roseberry"], ["Londres", "Paris", "Angleterre", "Epsom", "Europe"], ["Foreign Office", "L'Information"]),
    "l_humanite-1914-07-26-111": (["San Giuliano"], ["Italie", "Autriche", "Balkans", "Adriatique", "Rome", "Fiuggi"], ["Corriere délia Sera", "Giornale d'Italia"]),
    "l_humanite-1914-07-27-094": (["John Simon"], ["Europe", "Manchester", "Angleterre"], []),
    "l_humanite-1914-07-28-108": ([], ["Francfort", "Allemagne"], ["Gazette de Francfort"]),
    "l_humanite-1914-07-29-122": ([], [], ["C.G.T.", "Internationale"]),
    "l_humanite-1914-07-30-029": (["Asquith"], ["Londres"], ["Banque d'Angleterre", "Amirauté"]),
    "l_humanite-1914-07-31-216": ([], ["Maison commune", "rue de Bretagne"], ["Fédération nationale des Jeunesses socialistes", "Comité d'entente des jeunesses socialistes de la Seine", "groupe des Femmes socialistes"]),
    "l_humanite-1914-08-01-104": (["Lauche", "Jaurès", "Jules Guesde", "Bon"], ["Clichy"], []),
    "l_humanite-1914-08-01-028": ([], ["rue du Mail"], []),
    "l_humanite-1914-08-01-077": ([], ["Russie", "Vienne", "Klotjova"], []),
    "l_humanite-1914-08-02-074": (["Millevoye", "Jaurès"], [], []),
    "l_humanite-1914-08-03-047": (["Bertrand", "Vandervelde", "Jaurès"], ["Bruxelles", "Maison du Peuple de Bruxelles"], ["Conseil général du Parti ouvrier", "Groupe socialiste"]),
    "l_humanite-1914-08-03-079": (["Jaurès"], [], ["Confédération Générale du Travail", "Union des Syndicats de la Seine"]),
    "le_figaro-1914-08-07-133": ([], ["Paris", "Halles"], []),
    "le_figaro-1914-08-08-106": (["von Winterfeld"], ["Paris", "Grisolles"], ["Nationale"]),
    "le_figaro-1914-08-09-014": (["Gabriel Hanotaux"], ["Alsace", "Altkirch", "Mulhouse", "France"], ["Académie française", "ministère de la guerre"]),
    "l_humanite-1914-08-19-040": ([], ["Bruxelles", "Angleterre", "Paris", "Londres"], ["Le Soir", "Haras"]),
    "l_humanite-1914-08-20-055": ([], ["Belfort", "Saint-Gosme"], ["conseil de guerre"]),
}

passages = pd.read_parquet(Path(__file__).parent.parent / "french-press-1914-passages" / "passages.parquet").set_index("id")
with open(Path(__file__).parent / "gold.jsonl", "w", encoding="utf8") as out:
    for passage_id, (people, places, organizations) in R.items():
        record = {
            "id": passage_id,
            "text": passages.text[passage_id],
            "people": people,
            "places": places,
            "organizations": organizations,
        }
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
print(len(R), "records")
