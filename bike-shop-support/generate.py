"""Write the made-up customer-support export of Biclou & Cie, a fictional bike shop.

Every ticket is written from the scenarios below (no real customer), each with several
message phrasings and several replies that follow `charte.md`. The noise of a real
support tool's export is then injected, at the rates of the README: rows exported
twice, re-sent messages, unusable replies, open tickets, an agent who breaks the
charter, the return policy before 2025-06-01, personal data, channel artefacts (HTML,
phone signatures, quoted mails), typos, messages in English and messy labels.

`python generate.py` (standard library only) rewrites tickets.csv and test.jsonl and
prints the counts of each category and each kind of noise; the seed makes it
reproducible. The text sits in `FR` (and `EN`, the English messages of the export),
by scenario: an English version of the dataset only needs `EN` filled for every
scenario.
"""

import csv
import json
import random
import re
import string
import unicodedata
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 2026
HERE = Path(__file__).parent
START = date(2024, 9, 1)
END = date(2026, 8, 31)
POLICY_CHANGE = date(2025, 6, 1)  # return window: 14 days before, 30 days after
TEST_FROM = date(2026, 3, 1)
N_BASE = 2235  # tickets before the re-sent messages and the rows exported twice
TEST_QUOTAS = {
    "information": 40,
    "livraison": 28,
    "reparation": 22,
    "retour": 18,
    "location": 16,
    "facturation": 14,
    "compte": 12,
}

# Rates of the noise, as a share of the base tickets (exact duplicates: of all rows).
RATES = {
    "near_duplicate": 0.032,
    "exact_duplicate": 0.04,
    "unusable": 0.05,
    "open": 0.015,  # plus 30 of the last 45 days
    "bad_agent": 0.07,
    "english": 0.08,  # of the tickets of the scenarios EN covers: 4 % of all
    "email": 0.055,
    "phone": 0.05,
    "address": 0.012,
    "typos": 0.10,
    "no_accents": 0.06,
    "shouting": 0.012,
    "html": 0.55,  # of the formulaire messages
    "mobile_signature": 0.25,  # of the email messages
    "quoted_mail": 0.07,  # of the email messages
    "label_empty": 0.06,
    "label_spelling": 0.05,
    "satisfaction_empty": 0.28,  # of the resolved tickets, the others have none
}

CATEGORIES = {
    "information": 0.30,
    "livraison": 0.20,
    "reparation": 0.15,
    "retour": 0.12,
    "location": 0.10,
    "facturation": 0.08,
    "compte": 0.05,
}
# Monthly weights (January to December): rentals in summer, repairs in spring.
SEASONS = {
    "location": [0.2, 0.2, 0.5, 1.0, 1.5, 1.9, 2.3, 2.3, 1.4, 0.6, 0.2, 0.2],
    "reparation": [0.7, 0.7, 1.1, 1.4, 1.3, 1.2, 1.0, 0.9, 1.0, 0.9, 0.8, 0.7],
    "default": [0.8, 0.8, 1.0, 1.2, 1.2, 1.1, 1.0, 0.9, 1.1, 1.0, 1.0, 1.3],
}

VILLES = ["Lille", "Amiens", "Nice", "Marseille", "Nantes", "Rennes"]
CODES_POSTAUX = {
    "Lille": "59000",
    "Amiens": "80000",
    "Nice": "06000",
    "Marseille": "13005",
    "Nantes": "44000",
    "Rennes": "35000",
}
VELOS = [
    ("Biclou Urbain 3", 649.0),
    ("Biclou Rando 28", 899.0),
    ("Biclou Gravel G2", 1290.0),
    ("Biclou Route R7", 1490.0),
    ("Biclou Trail 29", 1190.0),
    ("Biclou Pliant P1", 549.0),
    ("Biclou Junior 24", 349.0),
]
VELOS_E = [
    ("Biclou Urbain E5", 1899.0),
    ("Biclou Rando E7", 2490.0),
    ("Biclou Cargo E8", 3290.0),
    ("Biclou Pliant E2", 1590.0),
]
# (French name, English name, price): all masculine, starting with a consonant, so
# that "le {accessoire}" and "un {accessoire}" read right.
ACCESSOIRES = [
    ("casque Urbain", "Urbain helmet", 59.9),
    ("cadenas en U Costaud", "Costaud U-lock", 39.9),
    ("porte-bagages Rando", "Rando rear rack", 44.9),
    ("phare LED Lumen", "Lumen LED light", 29.9),
    ("siège enfant Mini", "Mini child seat", 89.9),
    ("panier avant Osier", "Osier front basket", 34.9),
    ("compteur GPS Trace", "Trace GPS computer", 129.0),
    ("garde-boue Ville", "Ville mudguard set", 24.9),
    ("sac de cadre Bivouac", "Bivouac frame bag", 49.9),
    ("gonfleur à pied Pression", "Pression floor pump", 32.9),
]
ARTICLES_TAILLE = [
    ("casque Urbain", "Urbain helmet"),
    ("maillot Biclou", "Biclou jersey"),
    ("blouson de pluie Averse", "Averse rain jacket"),
    ("coupe-vent Mistral", "Mistral windbreaker"),
    ("cuissard Confort", "Confort cycling bib"),
]
TAILLES = ["S", "M", "L", "XL"]
NB = ["deux", "trois", "quatre"]

AGENTS = ["Sophie", "Karim", "Julien", "Nadia", "Thomas", "Léa", "Mehdi"]
BAD_AGENT = "Jordan"
ENGLISH_AGENTS = ["Nadia", "Julien", "Sophie"]

PRENOMS_F = [
    "Claire",
    "Julie",
    "Sandrine",
    "Nathalie",
    "Isabelle",
    "Céline",
    "Aurélie",
    "Émilie",
    "Sophie",
    "Hélène",
    "Laura",
    "Manon",
    "Chloé",
    "Inès",
    "Sarah",
    "Lucie",
    "Anne",
    "Marion",
    "Pauline",
    "Élodie",
    "Agnès",
    "Martine",
    "Brigitte",
    "Sylvie",
    "Yasmina",
    "Fatima",
    "Léna",
    "Océane",
    "Margaux",
    "Jeanne",
]
PRENOMS_M = [
    "Thomas",
    "Nicolas",
    "Julien",
    "Pierre",
    "Antoine",
    "Mathieu",
    "Sébastien",
    "Olivier",
    "François",
    "Laurent",
    "Philippe",
    "Romain",
    "Hugo",
    "Lucas",
    "Maxime",
    "Benoît",
    "Karim",
    "Youssef",
    "Mehdi",
    "Arnaud",
    "Vincent",
    "Gérard",
    "Bernard",
    "Alain",
    "Théo",
    "Louis",
    "Bastien",
    "Rémi",
    "Cédric",
    "Yann",
]
NOMS = [
    "Martin",
    "Bernard",
    "Dubois",
    "Durand",
    "Lefebvre",
    "Moreau",
    "Laurent",
    "Simon",
    "Michel",
    "Lefèvre",
    "Leroy",
    "Roux",
    "David",
    "Bertrand",
    "Morel",
    "Fournier",
    "Girard",
    "Bonnet",
    "Dupont",
    "Lambert",
    "Fontaine",
    "Rousseau",
    "Vincent",
    "Muller",
    "Lemaire",
    "Faure",
    "André",
    "Mercier",
    "Blanc",
    "Guérin",
    "Boyer",
    "Garnier",
    "Chevalier",
    "François",
    "Legrand",
    "Gauthier",
    "Perrin",
    "Robin",
    "Clément",
    "Morin",
    "Nicolas",
    "Henry",
    "Roussel",
    "Mathieu",
    "Gautier",
    "Masson",
    "Marchand",
    "Duval",
    "Denis",
    "Dumont",
    "Lemoine",
    "Le Goff",
    "Le Gall",
    "Benali",
    "Haddad",
    "Nguyen",
    "Da Silva",
    "Ferreira",
    "Caron",
    "Vasseur",
]
FIRST_NAMES_F = ["Emily", "Sarah", "Laura", "Hannah", "Megan", "Charlotte", "Grace"]
FIRST_NAMES_M = ["James", "Daniel", "Oliver", "Peter", "Thomas", "Henry", "Jack"]
LAST_NAMES = [
    "Carter",
    "Walker",
    "Mitchell",
    "Hughes",
    "Bennett",
    "Grant",
    "Price",
    "Reed",
    "Foster",
    "Collins",
    "Parker",
    "Turner",
    "Morgan",
    "Hayes",
]
DOMAINES = ["example.com", "example.org", "mail.test", "exemple.fr"]
RUES = [
    "rue des Glycines",
    "avenue des Peupliers",
    "rue du Moulin",
    "boulevard des Tilleuls",
    "impasse des Lilas",
    "rue de la Fontaine",
    "allée des Cerisiers",
    "rue des Écoles",
]
MOIS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# What a reply opens and closes with, per the charter.
GREETINGS = {
    "fr": {
        "F": "Bonjour Madame {nom},",
        "M": "Bonjour Monsieur {nom},",
        None: "Bonjour,",
    },
    "en": {"F": "Hello Ms {nom},", "M": "Hello Mr {nom},", None: "Hello,"},
}
SIGN_OFF = {
    "fr": "Bonne journée,\nL'équipe Biclou & Cie",
    "en": "Have a nice day,\nThe Biclou & Cie team",
}
CLOSERS = {
    "fr": [
        "Merci",
        "Merci d'avance",
        "Cordialement",
        "Bien cordialement",
        "Bonne journée",
        "Merci de votre aide",
        "",
    ],
    "en": ["Thanks", "Kind regards", "Best regards", "Many thanks", ""],
}
# The form's drop-down list, which becomes the subject of a formulaire ticket.
FORM_SUBJECTS = {
    "information": "Question sur un produit ou un magasin",
    "livraison": "Suivi de commande",
    "reparation": "Atelier et réparations",
    "retour": "Retour ou échange",
    "location": "Location de vélos",
    "facturation": "Facturation et paiement",
    "compte": "Mon compte",
}
FORM_OTHER = "Autre demande"
CHAT_SUBJECT = {"fr": "Conversation chat", "en": "Conversation chat"}

# Slots a reply may use without the message naming them: they follow from the
# message (the order number, if given) or from the ticket's date (the return window).
DERIVED = {"commande", "achat", "delai_retour", "commande_en", "delai_retour_en"}

# Scenarios: label, weight within the category, subjects, messages, reply bodies (the
# text between the greeting and the sign-off, which `reply()` adds). A reply only
# uses the slots every message of its scenario names (checked by `check_templates`).
FR = {
    # information
    "horaires": {
        "categorie": "information",
        "priorite": "basse",
        "poids": 0.25,
        "objets": ["Horaires d'ouverture", "Horaires magasin {ville}", "Ouverture"],
        "messages": [
            "Bonjour,\n\nQuels sont les horaires d'ouverture de votre magasin {de_ville} ? Je voudrais passer voir les vélos cette semaine.",
            "vous etes ouverts le lundi a {ville} ?",
            "Bonjour, je travaille jusqu'à 18 h et je voudrais savoir si le magasin {de_ville} ferme tard le samedi. Est-ce qu'il faut prendre rendez-vous pour essayer un vélo ?",
            "Bonjour,\n\nHier vers 9 h 30, votre boutique {de_ville} était fermée, alors que je pensais que vous ouvriez à 9 h comme les autres magasins de la rue. Du coup je ne sais plus trop. Vous pouvez me redonner vos horaires exacts ? Et est-ce que c'est pareil dans tous les magasins ?",
            "Horaires {ville} svp",
            "Bonjour, le magasin {de_ville} est-il ouvert le dimanche ? Je ne suis disponible que le week-end.",
        ],
        "reponses": [
            "Notre magasin {de_ville} vous accueille du mardi au samedi, de 10 h à 19 h, sans interruption. Il est fermé le dimanche et le lundi. Tous nos magasins suivent les mêmes horaires, et l'essai d'un vélo se fait sans rendez-vous. Nos conseillers vous aideront volontiers à choisir le modèle qui vous convient.",
            "Tous nos magasins, dont celui {de_ville}, sont ouverts du mardi au samedi de 10 h à 19 h. Ils sont fermés le dimanche et le lundi. Vous pouvez passer sans rendez-vous, y compris pour essayer un vélo : présentez-vous simplement à l'accueil, un conseiller s'occupera de vous.",
            "Le magasin Biclou & Cie {de_ville} est ouvert du mardi au samedi, de 10 h à 19 h, et fermé le dimanche et le lundi, comme nos cinq autres magasins. Aucun rendez-vous n'est nécessaire, même pour un essai : il vous suffit de venir aux heures d'ouverture.",
        ],
    },
    "stock": {
        "categorie": "information",
        "priorite": "basse",
        "poids": 0.25,
        "objets": [
            "Disponibilité {velo}",
            "Stock magasin {ville}",
            "Question sur le {velo}",
        ],
        "messages": [
            "Bonjour,\n\nEst-ce que le {velo} est disponible en taille {taille_cadre} dans votre magasin {de_ville} ? J'aimerais l'essayer avant de l'acheter.",
            "{velo} taille {taille_cadre} en stock à {ville} ?",
            "Bonjour, je cherche un {velo} en {taille_cadre}, sur le site il est indiqué indisponible. Est-ce qu'il en reste en magasin à {ville} ? Et sinon, vous en recevez quand ?",
            "Bonjour à toute l'équipe, ma fille entre au lycée en septembre et on a décidé de lui offrir un vélo pour qu'elle y aille seule, c'est à 4 km de la maison. On a repéré le {velo} sur votre site, taille {taille_cadre}. Avant de nous déplacer jusqu'à {ville}, on voudrait être sûrs qu'il est bien en magasin.",
            "Bonjour, vous avez encore le {velo} en {taille_cadre} à {ville} ? Je peux le réserver ?",
        ],
        "reponses": [
            "Le stock de chaque magasin est affiché en temps réel sur la fiche du {velo}, rubrique « Disponibilité en magasin » : sélectionnez la taille {taille_cadre} puis le magasin {de_ville}. Si le vélo y est disponible, réservez-le en ligne : nous le gardons de côté 3 jours pour votre essai. Le magasin est ouvert du mardi au samedi, de 10 h à 19 h.",
            "Pour connaître la disponibilité du {velo} en taille {taille_cadre} à {ville}, le plus sûr est sa fiche produit sur notre site, qui affiche le stock de chaque magasin en temps réel. S'il est en stock, réservez-le en ligne : il vous attend 3 jours en boutique. Sinon, la fiche indique la date du prochain réapprovisionnement.",
            "Merci pour votre intérêt pour le {velo}. Sa disponibilité en taille {taille_cadre} dans notre magasin {de_ville} est indiquée sur sa fiche produit, mise à jour en temps réel. Nous vous conseillons de le réserver en ligne avant de vous déplacer : il sera gardé 3 jours en magasin, le temps de l'essayer. Nos conseillers vous attendent du mardi au samedi, de 10 h à 19 h.",
        ],
    },
    "taille": {
        "categorie": "information",
        "priorite": "basse",
        "poids": 0.2,
        "derives": {"taille_cadre"},  # from the height the message gives
        "objets": ["Quelle taille ?", "Taille du {velo}", "Conseil taille de cadre"],
        "messages": [
            "Bonjour,\n\nJe mesure {hauteur} et j'hésite entre deux tailles pour le {velo}. Laquelle me conseillez-vous ?",
            "quelle taille pour {hauteur} ? {velo}",
            "Bonjour, je voudrais commander le {velo} pour mon mari qui fait {hauteur}. Le guide des tailles donne une taille mais un ami me dit de prendre plus grand. Qui croire ? Et si la taille ne va pas, je peux l'échanger ?",
            "Bonjour, je fais {hauteur} avec des jambes plutôt longues, je cherche un vélo pour aller au travail (environ 8 km par jour). Le {velo} m'intéresse, mais je ne sais pas quelle taille de cadre choisir, votre site propose S, M, L et XL.",
            "Bonjour, quelle taille de {velo} pour une personne de {hauteur} ?",
        ],
        "reponses": [
            "Pour une taille de {hauteur}, nous vous conseillons le {velo} en taille {taille_cadre}, selon notre guide des tailles. Le mieux reste de l'essayer en magasin, sans rendez-vous, du mardi au samedi de 10 h à 19 h. Si vous commandez en ligne et que la taille ne convient pas, le vélo non utilisé, dans son emballage, peut nous être retourné jusqu'à {delai_retour} après la livraison.",
            "D'après notre guide des tailles, le {velo} en taille {taille_cadre} correspond à votre taille de {hauteur}. La longueur des jambes peut faire varier ce choix : un essai en magasin permet de régler la hauteur de selle et de confirmer la taille. Si vous commandez en ligne, vous disposez de {delai_retour} après la livraison pour retourner le vélo non utilisé, dans son emballage.",
            "Pour {hauteur}, notre guide des tailles recommande la taille {taille_cadre} sur le {velo}. Nos conseillers peuvent le vérifier avec vous lors d'un essai, dans l'un de nos six magasins, du mardi au samedi de 10 h à 19 h. En cas de commande en ligne, un vélo non utilisé et dans son emballage peut être retourné dans les {delai_retour} suivant la livraison.",
        ],
    },
    "choix_vae": {
        "categorie": "information",
        "priorite": "basse",
        "poids": 0.15,
        "objets": [
            "Conseil vélo électrique",
            "Quel VAE choisir ?",
            "Question {velo_e}",
        ],
        "messages": [
            "Bonjour, je voudrais passer au vélo électrique pour mes trajets domicile-travail, {km} km aller. Le {velo_e} est-il adapté ? Et combien de temps dure la batterie ?",
            "Bonjour,\n\nJ'hésite entre le {velo_e} et un vélo classique pour faire {km} km par jour. Je n'ai jamais eu de vélo électrique. Est-ce que la batterie est garantie ? On m'a dit qu'il fallait la changer au bout de deux ans...",
            "{velo_e} pour {km} km par jour, ça le fait ?",
            "Bonjour, avec mon conjoint on pense acheter un {velo_e} pour remplacer la deuxième voiture. Il y a {km} km jusqu'à son travail, avec une bonne côte au milieu. Vous pensez que c'est faisable toute l'année ?",
        ],
        "reponses": [
            "Pour un trajet de {km} km, le {velo_e} est un bon choix : son assistance rend les montées et le vent bien plus faciles. Sa batterie est garantie 2 ans ou 500 cycles de charge, et le cadre 5 ans. Le plus simple est de l'essayer dans l'un de nos magasins, sans rendez-vous, du mardi au samedi de 10 h à 19 h : un conseiller vous expliquera son autonomie et son entretien.",
            "Pour {km} km par trajet, le {velo_e} convient très bien, confortable et facile à vivre au quotidien. Sa batterie est garantie 2 ans ou 500 cycles, les pièces et la main-d'œuvre 2 ans, et le cadre 5 ans. Venez l'essayer dans l'un de nos six magasins, du mardi au samedi de 10 h à 19 h : nos conseillers vous aideront à régler l'assistance selon votre parcours.",
        ],
    },
    "garantie_info": {
        "categorie": "information",
        "priorite": "basse",
        "poids": 0.15,
        "objets": ["Question garantie", "Garantie batterie", "Durée de garantie"],
        "messages": [
            "Bonjour, quelle est la durée de garantie sur vos vélos électriques ? Et sur la batterie ?",
            "Bonjour,\n\nAvant d'acheter un vélo chez vous, je voudrais savoir ce que couvre la garantie : le cadre, les pièces, la main-d'œuvre ? Pendant combien de temps ?",
            "garantie cadre combien d'années ?",
            "Bonjour, j'ai acheté un vélo électrique chez vous il y a un an et demi, juste pour savoir : si la batterie lâche, elle est encore couverte ? Elle a fait environ 300 recharges.",
        ],
        "reponses": [
            "Nos vélos sont garantis 2 ans pièces et main-d'œuvre, et leur cadre 5 ans. La batterie des vélos électriques est garantie 2 ans ou 500 cycles de charge, au premier des deux termes atteint. En cas de souci, apportez votre vélo dans l'un de nos magasins : le diagnostic est gratuit, et un devis vous est remis avant toute intervention hors garantie.",
            "La garantie Biclou & Cie couvre les pièces et la main-d'œuvre pendant 2 ans, et le cadre pendant 5 ans. Pour un vélo électrique, la batterie est couverte 2 ans ou 500 cycles de charge, selon ce qui arrive en premier. Conservez votre facture, disponible dans votre espace client : elle vous sera demandée en magasin si vous faites jouer la garantie.",
        ],
    },
    # livraison
    "colis_retard": {
        "categorie": "livraison",
        "priorite": "normale",
        "poids": 0.35,
        "commande_il_y_a": (8, 12),
        "objets": ["Commande non reçue", "Où est mon colis ?", "Retard de livraison"],
        "messages": [
            "Bonjour,\n\nJ'ai passé la commande {cmd} le {date_commande} et je n'ai toujours rien reçu. Le suivi n'a pas bougé depuis deux jours. Pouvez-vous me dire où en est mon colis ?",
            "Commande {cmd} toujours pas arrivée. C'est normal ?",
            "Bonjour, j'ai commandé un {accessoire} le {date_commande}{cmd_opt}, le site annonçait 3 à 5 jours et je n'ai rien. J'en ai besoin pour ce week-end. Vous pouvez faire quelque chose ?",
            "Franchement c'est long. J'ai commandé le {date_commande}{cmd_opt}, rien reçu, aucune nouvelle. J'attends une réponse rapide.",
            "Bonjour,\n\nPetite question au sujet de ma commande{cmd_apres} passée le {date_commande} : le suivi indique « en cours d'acheminement » depuis plusieurs jours. Est-ce que je dois m'inquiéter ?",
        ],
        "reponses": [
            "Nous sommes désolés pour l'attente concernant {commande}. Nos livraisons prennent habituellement 3 à 5 jours ouvrés, mais un transporteur peut prendre quelques jours de retard. Le lien de suivi de votre e-mail d'expédition indique son avancement. Si vous n'avez rien reçu 10 jours ouvrés après l'expédition, répondez à ce message : nous ouvrirons une enquête auprès du transporteur.",
            "Merci pour votre message au sujet de {commande}. Le délai de livraison habituel est de 3 à 5 jours ouvrés, et certains colis prennent un peu plus de temps. Sans livraison 10 jours ouvrés après l'expédition, nous ouvrons une enquête auprès du transporteur, puis vous proposons un nouvel envoi ou un remboursement. Recontactez-nous simplement passé ce délai.",
            "Nous comprenons votre impatience au sujet de {commande}. Nos colis sont livrés en 3 à 5 jours ouvrés en temps normal, et le vôtre a pris un peu de retard chez le transporteur. S'il n'est pas arrivé 10 jours ouvrés après l'expédition, écrivez-nous : nous lancerons une enquête auprès du transporteur, puis un nouvel envoi ou un remboursement.",
        ],
    },
    "colis_perdu": {
        "categorie": "livraison",
        "priorite": "haute",
        "poids": 0.25,
        "commande_il_y_a": (18, 32),
        "objets": ["Colis perdu ?", "Commande jamais reçue", "Toujours rien reçu !"],
        "messages": [
            "Bonjour,\n\nMa commande {cmd} date du {date_commande} et je n'ai toujours rien reçu, le suivi est bloqué depuis plus de deux semaines. Je commence à penser que le colis est perdu. Que comptez-vous faire ?",
            "Ça fait 3 semaines que j'attends ma commande {cmd}. 3 SEMAINES. Je veux mon colis ou mon argent.",
            "Bonjour, toujours pas de nouvelles de mon {article} commandé le {date_commande}{cmd_opt}. Le transporteur me renvoie vers vous, vous me renvoyez vers le transporteur. Qui s'occupe de mon colis ?",
            "Bonjour, ma commande{cmd_apres} du {date_commande} n'a jamais été livrée. Le suivi n'a plus bougé depuis deux semaines et personne ne me répond. Merci de regarder.",
        ],
        "reponses": [
            "Nous sommes désolés : {commande} aurait dû vous parvenir depuis longtemps. Au-delà de 10 jours ouvrés de retard, nous ouvrons une enquête auprès du transporteur, et c'est fait dès aujourd'hui. À son issue, nous vous proposerons un nouvel envoi ou un remboursement. Vous n'avez rien à faire d'ici là : nous vous écrirons dès que nous aurons sa réponse.",
            "Merci de nous avoir signalé ce retard sur {commande}. Votre colis a dépassé de plus de 10 jours ouvrés le délai prévu : nous ouvrons aujourd'hui une enquête auprès du transporteur. Dès sa conclusion, vous aurez le choix entre un nouvel envoi et un remboursement. Nous reviendrons vers vous par e-mail dès que nous aurons sa réponse.",
            "Nous comprenons votre agacement, et nous prenons le relais auprès du transporteur pour {commande}. Un colis en retard de plus de 10 jours ouvrés fait l'objet d'une enquête, que nous venons d'ouvrir. À son issue, nous vous proposerons un nouvel envoi ou un remboursement, comme vous le préférerez. Nous reviendrons vers vous par e-mail dès sa conclusion.",
        ],
    },
    "colis_abime": {
        "categorie": "livraison",
        "priorite": "normale",
        "poids": 0.2,
        "objets": ["Colis abîmé", "Produit arrivé cassé", "Livraison endommagée"],
        "messages": [
            "Bonjour,\n\nJ'ai reçu ma commande {cmd} ce matin mais le carton était écrasé et le {accessoire} est abîmé. Comment faire ?",
            "Colis arrivé abîmé, {accessoire} cassé. Je fais quoi ?",
            "Bonjour, le {velo} est arrivé hier, le carton était déchiré sur le côté, il y a une grosse rayure sur le cadre et le garde-boue est tordu. Quelle déception, c'était un cadeau. Est-ce que vous pouvez m'en envoyer un autre ?",
            "Bonjour, commande {cmd} reçue mais le {accessoire} a une pièce cassée, sûrement pendant le transport. Vous pouvez me le remplacer ?",
        ],
        "reponses": [
            "Nous sommes désolés que {commande} soit arrivée abîmée. Envoyez-nous en réponse à ce message deux ou trois photos du colis et du produit endommagé : dès réception, nous vérifions et vous envoyons un produit de remplacement, sans frais pour vous. Gardez le produit et son emballage d'ici là, le transporteur peut nous les demander.",
            "Merci de nous avoir prévenus, et désolés pour ce colis endommagé. Pour traiter {commande}, nous avons besoin de photos du carton et du produit abîmé : joignez-les simplement à votre réponse. Après vérification, nous vous proposerons un remplacement. Conservez l'emballage d'origine en attendant notre retour.",
        ],
    },
    "changer_adresse": {
        "categorie": "livraison",
        "priorite": "normale",
        "poids": 0.1,
        "objets": [
            "Changement d'adresse",
            "Erreur d'adresse de livraison",
            "Modifier l'adresse",
        ],
        "messages": [
            "Bonjour, je viens de passer la commande {cmd} et j'ai fait une erreur dans l'adresse de livraison. Est-il possible de la modifier ?",
            "Bonjour,\n\nJe déménage la semaine prochaine, est-ce que je peux faire livrer ma commande{cmd_apres} à ma nouvelle adresse plutôt qu'à l'ancienne ?",
            "erreur d'adresse sur ma commande{cmd_apres}, comment corriger ?",
        ],
        "reponses": [
            "Si {commande} n'est pas encore expédiée, nous pouvons modifier l'adresse de livraison. Répondez à ce message en indiquant la nouvelle adresse complète : nous la mettons à jour et vous confirmons le changement par e-mail. Si le colis est déjà parti, nous demanderons une redirection au transporteur, ce qui peut ajouter un ou deux jours au délai habituel de 3 à 5 jours ouvrés.",
            "Pas d'inquiétude : l'adresse de {commande} peut être corrigée tant que le colis n'a pas quitté notre entrepôt. Indiquez-nous la nouvelle adresse en réponse à ce message, et nous vous enverrons une confirmation dès la modification faite. Notre délai de livraison reste de 3 à 5 jours ouvrés à compter de l'expédition.",
        ],
    },
    "delai_info": {
        "categorie": "livraison",
        "priorite": "basse",
        "poids": 0.1,
        "objets": ["Délais de livraison", "Livraison avant le {date_evenement} ?"],
        "messages": [
            "Bonjour, si je commande le {velo} aujourd'hui, je le reçois quand ? Il me le faut avant le {date_evenement}.",
            "Bonjour,\n\nQuels sont vos délais de livraison pour un vélo ? Je voudrais l'avoir avant le {date_evenement}, c'est pour un anniversaire.",
            "délai de livraison ? besoin avant le {date_evenement}",
        ],
        "reponses": [
            "Nos commandes sont livrées en 3 à 5 jours ouvrés après leur expédition, vélos compris. Pour une livraison avant le {date_evenement}, nous vous conseillons de commander au moins une semaine avant cette date. Dès l'expédition, vous recevrez par e-mail un lien de suivi du colis. Vous pouvez aussi retirer votre vélo dans l'un de nos six magasins, selon le stock affiché sur sa fiche.",
            "Le délai de livraison est de 3 à 5 jours ouvrés, pour un vélo comme pour un accessoire. En commandant au moins une semaine avant le {date_evenement}, vous devriez le recevoir à temps, et un e-mail vous donnera le lien de suivi dès l'expédition. Si le temps presse, venez le chercher dans l'un de nos magasins, ouverts du mardi au samedi de 10 h à 19 h.",
        ],
    },
    # reparation
    "crevaison": {
        "categorie": "reparation",
        "priorite": "normale",
        "poids": 0.15,
        "objets": ["Crevaison", "Pneu crevé vélo neuf", "Crevaison après une semaine"],
        "messages": [
            "Bonjour,\n\nJ'ai acheté le {velo} il y a une semaine et j'ai déjà crevé à l'arrière. C'est normal ? C'est couvert par la garantie ?",
            "Crevé au bout de 8 jours avec mon {velo}. Super qualité...",
            "Bonjour, une crevaison sur mon {velo} neuf, acheté au magasin {de_ville}. Je peux passer pour que vous regardiez ? Il faut prendre rendez-vous ?",
            "Bonjour, alors voilà, j'ai mon {velo} depuis une dizaine de jours, je fais le trajet jusqu'au boulot tous les matins, et hier soir pneu à plat. J'ai regonflé, ce matin rebelote. Le bricolage, ce n'est pas mon fort, et je ne voudrais pas abîmer quelque chose. Qu'est-ce que vous me conseillez ?",
        ],
        "reponses": [
            "Nous sommes désolés pour cette crevaison sur votre {velo}. Apportez-le dans l'un de nos magasins, sans rendez-vous, du mardi au samedi de 10 h à 19 h : le diagnostic est gratuit. Si le pneu ou la chambre à air présente un défaut, la réparation est couverte par la garantie de 2 ans ; sinon, nous vous remettrons un devis avant toute intervention.",
            "Une crevaison peut arriver dès les premiers jours, souvent à cause d'un petit débris coincé dans le pneu. Passez avec votre {velo} dans l'un de nos ateliers : le diagnostic est gratuit et sans rendez-vous. Un défaut du pneu ou de la chambre à air est pris en charge par la garantie ; dans le cas contraire, un devis vous sera proposé avant toute réparation.",
        ],
    },
    "freins_grincent": {
        "categorie": "reparation",
        "priorite": "normale",
        "poids": 0.16,
        "objets": ["Freins qui grincent", "Bruit de freins", "Freins {velo}"],
        "messages": [
            "Bonjour,\n\nMes freins grincent beaucoup depuis quelques jours sur mon {velo}, surtout sous la pluie. Ils freinent toujours bien mais le bruit est pénible. Faut-il les changer ?",
            "{velo} : les freins couinent à chaque freinage, ça freine mais c'est insupportable",
            "Bonjour, les freins de mon {velo} font un bruit aigu quand je freine. Combien coûte une révision des freins et combien de temps faut-il laisser le vélo ?",
            "Bonjour, depuis que j'ai roulé sous la pluie la semaine dernière, le frein arrière de mon {velo} siffle à chaque arrêt. Le freinage est normal, c'est juste le bruit. Vous pouvez y jeter un œil ?",
        ],
        "reponses": [
            "Un grincement de freins vient le plus souvent de plaquettes encrassées ou mal alignées, sans danger tant que le freinage reste efficace. Déposez votre {velo} dans l'un de nos ateliers : le diagnostic est gratuit, un devis vous est proposé avant toute intervention, et le vélo est prêt sous 5 jours ouvrés. Si vous sentez le freinage faiblir, arrêtez de rouler et prévenez-nous.",
            "Merci pour votre message. Des freins qui grincent mais freinent bien ne sont pas dangereux, mais méritent un réglage. Nos ateliers établissent un diagnostic gratuit de votre {velo} et vous remettent un devis avant toute intervention ; le délai est de 5 jours ouvrés. Vous pouvez déposer le vélo sans rendez-vous, du mardi au samedi de 10 h à 19 h.",
        ],
    },
    "freins_defaillants": {
        "categorie": "reparation",
        "priorite": "haute",
        "poids": 0.14,
        "objets": [
            "URGENT freins",
            "Freins qui ne freinent plus",
            "Problème de freins dangereux",
        ],
        "messages": [
            "Bonjour,\n\nCe matin en descente, mes freins n'ont presque pas répondu, j'ai dû mettre le pied par terre pour m'arrêter. C'est un {velo} acheté chez vous. Je n'ose plus rouler avec. Merci de me répondre vite.",
            "URGENT plus de freins sur mon {velo}, le levier arrière va jusqu'au guidon",
            "Bonjour, le frein avant de mon {velo} ne freine quasiment plus depuis hier, j'ai failli rentrer dans une voiture. Est-ce que c'est sous garantie ? Je peux passer à {ville} quand ?",
            "Bonjour, mon fils a le {velo} depuis trois mois et ses freins ne marchent presque plus, la poignée s'enfonce sans résistance. C'est dangereux, non ?",
        ],
        "reponses": [
            "Merci de nous avoir alertés : un freinage défaillant est un problème de sécurité. Ne roulez plus avec votre {velo} jusqu'à son contrôle. Déposez-le dans l'un de nos ateliers : les problèmes de freins sont pris en charge sous 48 h, avec un diagnostic gratuit. Si la panne relève de la garantie de 2 ans pièces et main-d'œuvre, la réparation ne vous coûtera rien.",
            "Votre sécurité passe avant tout : arrêtez de rouler avec votre {velo} dès maintenant. Un frein qui ne répond plus doit être contrôlé par notre atelier, qui prend en charge ce type de problème sous 48 h. Apportez le vélo dans le magasin de votre choix, du mardi au samedi de 10 h à 19 h ; le diagnostic est gratuit et un devis vous sera remis avant toute intervention hors garantie.",
        ],
    },
    "batterie_charge": {
        "categorie": "reparation",
        "priorite": "normale",
        "poids": 0.16,
        "objets": [
            "Batterie ne charge plus",
            "Problème de batterie",
            "Batterie {velo_e}",
        ],
        "messages": [
            "Bonjour,\n\nLa batterie de mon {velo_e} ne charge plus : le voyant reste éteint quand je la branche. Le vélo a {age_mois} mois. Que dois-je faire ?",
            "batterie {velo_e} ne charge plus, chargeur testé sur une autre prise, rien",
            "Bonjour, depuis quelques jours la batterie de mon {velo_e} ne dépasse plus 60 % de charge, et l'autonomie a beaucoup baissé. Elle est encore sous garantie ? Le vélo a {age_mois} mois.",
            "Bonjour, ma batterie de {velo_e} clignote en rouge quand je la mets en charge et ne se charge pas. C'est la batterie ou le chargeur ?",
        ],
        "reponses": [
            "Nous sommes désolés pour ce souci de batterie sur votre {velo_e}. La batterie est garantie 2 ans ou 500 cycles de charge, au premier terme atteint. Apportez le vélo, la batterie et son chargeur dans l'un de nos ateliers : le diagnostic est gratuit, et le vélo est prêt sous 5 jours ouvrés. Si la batterie est hors garantie, un devis vous sera remis avant toute intervention.",
            "Merci pour votre message. Pour comprendre ce qui bloque la charge, notre atelier doit tester la batterie et le chargeur de votre {velo_e} : déposez-les dans l'un de nos magasins, sans rendez-vous. Le diagnostic est gratuit et prend 5 jours ouvrés au plus. La batterie est couverte 2 ans ou 500 cycles ; au-delà, un devis vous est proposé avant toute réparation.",
        ],
    },
    "batterie_surchauffe": {
        "categorie": "reparation",
        "priorite": "haute",
        "poids": 0.1,
        "objets": [
            "Batterie brûlante",
            "URGENT batterie qui chauffe",
            "Batterie gonflée",
        ],
        "messages": [
            "Bonjour,\n\nHier soir la batterie de mon {velo_e} est devenue brûlante pendant la charge, avec une odeur de plastique. J'ai tout débranché. Est-ce dangereux ?",
            "Ma batterie {velo_e} chauffe énormément et a gonflé sur le côté. Je fais quoi ??",
            "Bonjour, en rentrant de balade la batterie de mon {velo_e} était très chaude, presque impossible à toucher, et l'écran affichait une erreur. J'ai peur que ça prenne feu dans le garage.",
        ],
        "reponses": [
            "Merci de nous avoir prévenus aussitôt : une batterie qui chauffe anormalement est un problème de sécurité. Ne la rechargez plus et ne roulez plus avec votre {velo_e}. Laissez-la à l'extérieur ou dans un endroit dégagé, loin de toute matière inflammable, puis apportez-la à l'un de nos ateliers : nous la prenons en charge sous 48 h. Elle est garantie 2 ans ou 500 cycles.",
            "Pour votre sécurité, arrêtez immédiatement d'utiliser et de recharger la batterie de votre {velo_e}. Laissez-la refroidir dans un endroit aéré, loin de ce qui peut brûler. Notre atelier traite ce type de problème en priorité, sous 48 h : déposez le vélo et la batterie dans le magasin de votre choix, du mardi au samedi de 10 h à 19 h. Le diagnostic est gratuit.",
        ],
    },
    "derailleur": {
        "categorie": "reparation",
        "priorite": "normale",
        "poids": 0.15,
        "objets": ["Vitesses qui sautent", "Réglage dérailleur", "Problème de chaîne"],
        "messages": [
            "Bonjour, les vitesses de mon {velo} sautent toutes seules, surtout en montée. Vous pouvez le régler ? Combien ça coûte ?",
            "Bonjour,\n\nDepuis ma dernière sortie, la chaîne de mon {velo} saute d'un pignon à l'autre et fait du bruit. Est-ce couvert par la garantie ? Je l'ai acheté il y a {age_mois} mois.",
            "vitesses qui sautent sur {velo}, besoin d'un réglage",
            "Bonjour, impossible de passer les petites vitesses sur mon {velo}, la manette force et rien ne se passe. J'ai une sortie prévue dans deux semaines, c'est jouable ?",
        ],
        "reponses": [
            "Des vitesses qui sautent demandent le plus souvent un simple réglage du dérailleur ou un câble à retendre. Déposez votre {velo} dans l'un de nos ateliers : le diagnostic est gratuit, et nous vous remettons un devis avant toute intervention. Si une pièce est défectueuse, elle est couverte par la garantie de 2 ans pièces et main-d'œuvre. Comptez 5 jours ouvrés.",
            "Merci pour votre message. Notre atelier peut régler la transmission de votre {velo} : apportez-le sans rendez-vous dans le magasin de votre choix, du mardi au samedi de 10 h à 19 h. Le diagnostic est gratuit, le devis vous est remis avant tout travail, et le vélo vous est rendu sous 5 jours ouvrés. Une pièce défectueuse est prise en charge par la garantie de 2 ans.",
        ],
    },
    "revision": {
        "categorie": "reparation",
        "priorite": "normale",
        "poids": 0.14,
        "objets": ["Révision", "Entretien de mon vélo", "Révision avant l'été"],
        "messages": [
            "Bonjour, je voudrais faire réviser mon {velo} avant l'été. Combien ça coûte et combien de temps vous le gardez ?",
            "Bonjour,\n\nFaites-vous la révision des vélos achetés ailleurs ? J'ai un {velo} d'occasion qui aurait besoin d'un bon entretien.",
            "révision complète {velo}, c'est possible ?",
            "Bonjour, mon {velo} n'a pas été entretenu depuis deux ans, la chaîne grince et les pneus sont usés. Je peux le déposer pour une révision complète ? Faut-il prendre rendez-vous ?",
        ],
        "reponses": [
            "Notre atelier révise volontiers votre {velo}, quel que soit le lieu d'achat. Déposez-le dans l'un de nos magasins, sans rendez-vous : nous faisons un diagnostic gratuit, puis vous remettons un devis avant toute intervention. Rien n'est fait sans votre accord. Comptez 5 jours ouvrés entre le dépôt et la restitution du vélo.",
            "Avec plaisir. Pour une révision de votre {velo}, le diagnostic est gratuit dans tous nos ateliers, et un devis détaillé vous est remis avant tout travail. Le vélo est ensuite prêt sous 5 jours ouvrés. Nos magasins vous accueillent sans rendez-vous du mardi au samedi, de 10 h à 19 h.",
        ],
    },
    # retour
    "mauvaise_taille": {
        "categorie": "retour",
        "priorite": "normale",
        "poids": 0.35,
        "objets": [
            "Échange de taille",
            "Retour taille {taille_recue}",
            "Mauvaise taille",
        ],
        "messages": [
            "Bonjour,\n\nJ'ai reçu le {article_taille} en taille {taille_recue} mais il est trop {petit_grand}. Je voudrais l'échanger contre un {taille_voulue}. Comment faire ?",
            "Bonjour, commande {cmd}, le {article_taille} en {taille_recue} ne me va pas, je voudrais le retourner. Il n'a pas été porté.",
            "{article_taille} taille {taille_recue} trop {petit_grand}, je veux échanger. Commande {cmd}.",
            "Bonjour, j'ai commandé le {article_taille} pour l'anniversaire de mon compagnon, en taille {taille_recue}, mais il lui est trop {petit_grand}. Il ne l'a essayé que deux minutes, l'étiquette est encore dessus et je n'ai pas jeté la boîte. Je peux le renvoyer par la poste ou il faut aller en magasin ? Et ça coûte combien ?",
        ],
        "reponses": [
            "Merci pour votre message concernant {commande}. Vous disposez de {delai_retour} après la livraison pour retourner le {article_taille}, à condition qu'il soit inutilisé et dans son emballage. Le retour est gratuit dans l'un de nos magasins, ou coûte 6,90 € par colis. Si vous le rapportez en magasin, nos conseillers vous proposeront directement la bonne taille.",
            "Nous sommes désolés que la taille ne convienne pas. Le {article_taille} de {commande} peut être retourné dans les {delai_retour} suivant la livraison, non utilisé et dans son emballage d'origine. Rapportez-le gratuitement dans l'un de nos six magasins, ou renvoyez-le par colis pour 6,90 €. Le remboursement intervient dans les 14 jours suivant la réception et le contrôle du retour à l'entrepôt.",
            "Pas de souci pour un échange de taille sur {commande}. Le {article_taille} doit nous revenir non utilisé, dans son emballage, dans les {delai_retour} suivant la livraison. Le plus rapide est de le rapporter dans l'un de nos magasins, où le retour est gratuit et l'échange immédiat selon le stock ; par colis, le retour coûte 6,90 €.",
        ],
    },
    "remboursement_attente": {
        "categorie": "retour",
        "priorite": "normale",
        "poids": 0.25,
        "objets": [
            "Remboursement non reçu",
            "Où en est mon remboursement ?",
            "Retour sans remboursement",
        ],
        "messages": [
            "Bonjour,\n\nJ'ai renvoyé le {article} le {date_retour}{cmd_opt} et je n'ai toujours pas reçu de remboursement. Pouvez-vous vérifier ?",
            "Remboursement de ma commande {cmd} toujours pas reçu. Retour envoyé il y a {jours_depuis_retour} jours.",
            "Bonjour, j'ai rapporté un {article} au magasin {de_ville} il y a {jours_depuis_retour} jours et je n'ai pas encore vu le remboursement sur mon compte. C'est normal ?",
            "Bonjour, je n'ai pas de nouvelles de mon retour{cmd_opt}. Le colis a été déposé il y a {jours_depuis_retour} jours et le suivi dit qu'il est arrivé chez vous. Quand vais-je recevoir le remboursement ?",
        ],
        "reponses": [
            "Merci pour votre message au sujet de {commande}. Le remboursement est versé dans les 14 jours qui suivent la réception et le contrôle du produit à notre entrepôt ; un retour déposé en magasin y est d'abord acheminé. Si ce délai est dépassé, répondez-nous avec la date de votre retour, et nous vérifierons où en est votre dossier.",
            "Nous comprenons votre attente concernant {commande}. Une fois le produit reçu et contrôlé à l'entrepôt, le remboursement est effectué sous 14 jours, sur le moyen de paiement utilisé lors de l'achat. Vous recevez un e-mail dès que le contrôle est terminé. Sans nouvelles de notre part passé ce délai, répondez à ce message : nous ferons le point avec l'entrepôt.",
        ],
    },
    "retour_utilise": {
        "categorie": "retour",
        "priorite": "normale",
        "poids": 0.2,
        "objets": [
            "Retour d'un produit utilisé",
            "Je peux rendre mon achat ?",
            "Retour",
        ],
        "messages": [
            "Bonjour, j'ai acheté un {article} il y a deux semaines, je l'ai utilisé trois fois et finalement il ne me plaît pas. Je peux le rendre ?",
            "Bonjour,\n\nPuis-je retourner un {article} que j'ai monté et essayé une fois ? Je l'ai remis dans son carton depuis.",
            "retour possible si déjà utilisé ? {article}",
        ],
        "reponses": [
            "Nous sommes désolés que le {article} ne vous convienne pas. Notre politique de retour s'applique aux produits inutilisés, dans leur emballage, dans les {delai_retour} suivant la livraison : un article déjà utilisé ne peut malheureusement pas être repris. En revanche, s'il présente un défaut, la garantie de 2 ans s'applique : apportez-le en magasin pour un diagnostic gratuit.",
            "Merci pour votre question. Un retour est possible dans les {delai_retour} après la livraison, pour un produit non utilisé et dans son emballage d'origine. Un {article} déjà utilisé ne remplit plus cette condition. Si vous constatez un défaut, en revanche, nos ateliers l'examinent gratuitement dans le cadre de la garantie de 2 ans pièces et main-d'œuvre.",
        ],
    },
    "retour_hors_delai": {
        "categorie": "retour",
        "priorite": "normale",
        "poids": 0.2,
        "objets": ["Demande de retour", "Retour {article}", "Remboursement"],
        "messages": [
            "Bonjour,\n\nJ'ai reçu le {article} il y a {jours_depuis} jours et je voudrais le retourner, il n'a jamais servi. C'est encore possible ?",
            "Bonjour, commande {cmd}, {article} livré il y a {jours_depuis} jours, jamais déballé, je souhaite un remboursement.",
            "retour d'un {article} reçu il y a {jours_depuis} jours, possible ?",
        ],
        "reponses": [
            "Merci pour votre message concernant {commande}. Le délai de retour est de {delai_retour} après la livraison : livré il y a {jours_depuis} jours, le {article} ne peut malheureusement plus être repris. Si le produit présente un défaut, la garantie de 2 ans pièces et main-d'œuvre s'applique : nos ateliers l'examineront gratuitement dans l'un de nos magasins.",
            "Nous comprenons votre demande au sujet de {commande}. Les retours sont acceptés pendant {delai_retour} après la livraison ; votre {article} ayant été livré il y a {jours_depuis} jours, ce délai est passé et nous ne pouvons pas le reprendre. En cas de défaut, la garantie de 2 ans s'applique : un diagnostic gratuit est possible dans l'un de nos magasins.",
        ],
    },
    # location
    "location_modif": {
        "categorie": "location",
        "priorite": "normale",
        "poids": 0.3,
        "objets": [
            "Modification de réservation",
            "Changer les dates de location",
            "Location {ville}",
        ],
        "messages": [
            "Bonjour,\n\nJ'ai réservé {nb_velos} vélos au magasin {de_ville} du {loc_debut} au {loc_fin}. Est-il possible de décaler la location au {loc_nouveau_debut} ?",
            "Bonjour, peut-on changer les dates de ma location à {ville} ? Prévue à partir du {loc_debut}, on voudrait commencer le {loc_nouveau_debut}.",
            "changement de date location {ville} : {loc_debut} -> {loc_nouveau_debut} possible ?",
            "Bonjour, nous avions réservé des vélos à {ville} à partir du {loc_debut}, mais notre train a été déplacé et nous n'arriverons que le {loc_nouveau_debut}. Est-ce qu'on peut garder la réservation en la décalant ? On ne voudrait pas perdre d'argent.",
        ],
        "reponses": [
            "Votre location à {ville} peut être déplacée au {loc_nouveau_debut}, selon les vélos disponibles à cette date. Les modifications et annulations sont gratuites jusqu'à 24 h avant le début de la location, prévu le {loc_debut}. Le plus simple est de changer les dates depuis votre espace client, rubrique « Mes locations » ; vous recevrez ensuite une confirmation par e-mail.",
            "Merci pour votre message. Vous pouvez décaler votre location à {ville} sans frais, tant que la demande nous parvient au moins 24 h avant son début, prévu le {loc_debut}. Modifiez les dates dans votre espace client, rubrique « Mes locations », ou répondez à ce message avec les nouvelles dates : nous vous confirmerons la disponibilité des vélos pour le {loc_nouveau_debut}.",
        ],
    },
    "location_tarifs": {
        "categorie": "location",
        "priorite": "basse",
        "poids": 0.3,
        "objets": ["Tarifs location", "Location vélo électrique", "Caution location"],
        "messages": [
            "Bonjour, combien coûte la location d'un vélo électrique pour un week-end à {ville} ? Faut-il une caution ?",
            "Bonjour,\n\nNous serons quatre à {ville} en vacances la semaine du {loc_debut}. Quels sont vos tarifs de location à la semaine ? Avez-vous des vélos électriques ?",
            "tarifs location à {ville} ?",
            "Bonjour, je voudrais louer deux vélos à {ville} pour une journée. Est-ce qu'on peut payer la caution en espèces ?",
        ],
        "reponses": [
            "Notre magasin {de_ville} loue des vélos à 15 € la journée ou 60 € la semaine, et des vélos électriques à 35 € la journée. Une caution de 300 € (800 € pour un vélo électrique) est demandée sous forme de pré-autorisation sur carte bancaire, faite en magasin et non débitée. Vous pouvez réserver en ligne ; l'annulation est gratuite jusqu'à 24 h avant.",
            "Voici nos tarifs de location à {ville} : 15 € par jour ou 60 € par semaine pour un vélo classique, 35 € par jour pour un vélo électrique. La caution, de 300 € ou de 800 € pour un vélo électrique, prend la forme d'une pré-autorisation sur carte bancaire au retrait du vélo. Réservez en ligne pour garantir la disponibilité : l'annulation reste gratuite jusqu'à 24 h avant le départ.",
        ],
    },
    "location_annulation": {
        "categorie": "location",
        "priorite": "normale",
        "poids": 0.15,
        "objets": ["Annulation location", "Annuler ma réservation"],
        "messages": [
            "Bonjour, je dois annuler ma réservation de location à {ville} du {loc_debut}, nous avons un empêchement. Est-ce que nous serons remboursés ?",
            "Annulation location {loc_debut} {ville} svp",
            "Bonjour,\n\nMalheureusement la météo annonce de la pluie toute la semaine, nous préférons annuler notre location de vélos électriques à {ville} prévue le {loc_debut}. Merci de nous confirmer l'annulation.",
        ],
        "reponses": [
            "C'est bien noté : votre location à {ville} du {loc_debut} peut être annulée sans frais, puisque la demande arrive plus de 24 h avant son début. Confirmez l'annulation depuis votre espace client, rubrique « Mes locations » : la somme éventuellement réglée en ligne vous sera intégralement rendue, et aucune caution ne sera demandée.",
            "Merci de nous avoir prévenus. L'annulation est gratuite jusqu'à 24 h avant le début de la location : celle du {loc_debut} à {ville} remplit cette condition. Annulez-la depuis votre espace client, rubrique « Mes locations », ou répondez à ce message pour que nous le fassions pour vous ; vous recevrez une confirmation par e-mail.",
        ],
    },
    "location_accident": {
        "categorie": "location",
        "priorite": "haute",
        "poids": 0.15,
        "objets": [
            "Accident avec un vélo de location",
            "Chute vélo loué",
            "Vélo de location abîmé",
        ],
        "messages": [
            "Bonjour,\n\nJ'ai eu un accident hier avec le vélo loué à {ville} : une voiture m'a coupé la route. Je n'ai que des égratignures mais la roue avant est voilée et le guidon tordu. Que dois-je faire ?",
            "Chute avec le vélo de location ce matin à {ville}, le dérailleur est cassé. Je le ramène comment ?",
            "Bonjour, mon fils est tombé avec le vélo électrique que nous avons loué à {ville}, il va bien mais le vélo est abîmé. On doit payer les réparations ? On ne sait pas trop quoi faire.",
        ],
        "reponses": [
            "Nous sommes désolés pour cet accident, et nous espérons que tout le monde va bien. Déclarez-le dans les 48 h, en répondant à ce message avec la date, le lieu et une description des faits, plus des photos du vélo si possible. Ramenez ensuite le vélo à notre magasin {de_ville} : notre atelier évaluera les dégâts avant toute décision sur la caution.",
            "Merci de nous avoir prévenus, et nous espérons que personne n'est sérieusement blessé. Un accident avec un vélo de location doit être déclaré dans les 48 h : envoyez-nous en réponse les circonstances, la date et quelques photos du vélo. Rapportez-le ensuite au magasin {de_ville}, sans le réparer vous-même. Notre atelier constatera les dégâts avant toute décision sur la caution.",
        ],
    },
    "location_vol": {
        "categorie": "location",
        "priorite": "haute",
        "poids": 0.1,
        "objets": ["Vol du vélo de location", "Vélo loué volé"],
        "messages": [
            "Bonjour,\n\nLe vélo que j'ai loué à {ville} a été volé cette nuit devant mon hôtel, alors qu'il était attaché avec l'antivol fourni. Que dois-je faire ?",
            "Vélo de location volé à {ville}, je fais comment ?",
            "Bonjour, c'est la catastrophe, on m'a volé le vélo électrique loué dans votre magasin {de_ville} pendant que je faisais mes courses. J'ai porté plainte. Est-ce que je vais perdre toute la caution ?",
        ],
        "reponses": [
            "Nous sommes désolés pour ce vol. Il doit être déclaré dans les 48 h : portez plainte auprès de la police ou de la gendarmerie, puis envoyez-nous le récépissé en réponse à ce message, avec la clé de l'antivol si vous l'avez encore. Notre magasin {de_ville} étudiera ensuite votre dossier et vous indiquera ce qui sera retenu sur la caution.",
            "Merci de nous avoir prévenus rapidement. Pour un vol de vélo de location, la déclaration doit nous parvenir dans les 48 h : joignez à votre réponse le récépissé de plainte et une courte description des faits. Le magasin {de_ville} examinera votre dossier avant toute décision sur la caution, et reviendra vers vous par e-mail.",
        ],
    },
    # facturation
    "double_debit": {
        "categorie": "facturation",
        "priorite": "haute",
        "poids": 0.35,
        "objets": ["Débité deux fois", "Double prélèvement", "Paiement en double"],
        "messages": [
            "Bonjour,\n\nJe viens de voir sur mon relevé que vous m'avez débité deux fois {montant} pour ma commande {cmd}. Pouvez-vous me rembourser le deuxième prélèvement ?",
            "Débité 2 fois !!! {montant} x2 pour la commande {cmd}. Remboursez-moi.",
            "Bonjour, ma banque m'indique deux paiements identiques de {montant} le même jour pour un seul achat chez vous{cmd_opt}. Est-ce une erreur de votre côté ?",
        ],
        "reponses": [
            "Nous sommes désolés pour ce double débit de {montant} sur {commande}. Nous vérifions dès aujourd'hui les deux paiements auprès de notre prestataire de paiement. Si le doublon est confirmé, le second débit vous sera remboursé dans les 5 jours ouvrés suivant cette vérification, sur le même moyen de paiement. Inutile de nous envoyer vos coordonnées bancaires : nous avons tout ce qu'il faut.",
            "Merci de nous avoir signalé ce double prélèvement de {montant} concernant {commande}. Notre service comptable vérifie la transaction ; si elle a bien été débitée deux fois, le montant en trop vous est remboursé sous 5 jours ouvrés après vérification, sur la carte utilisée pour l'achat. Vous recevrez un e-mail dès que le remboursement sera lancé.",
        ],
    },
    "facture": {
        "categorie": "facturation",
        "priorite": "normale",
        "poids": 0.35,
        "objets": ["Demande de facture", "Facture manquante", "Facture commande {cmd}"],
        "messages": [
            "Bonjour, pourriez-vous m'envoyer la facture de ma commande {cmd} ? Mon employeur me la demande pour le forfait mobilités durables.",
            "facture commande {cmd} svp",
            "Bonjour,\n\nJ'ai acheté un {velo} dans votre magasin {de_ville} et je n'ai pas reçu de facture, seulement le ticket de caisse. J'en ai besoin pour l'assurance.",
            "Bonjour, je ne trouve pas la facture de mon achat{cmd_opt}, il me la faut pour une demande d'aide à l'achat de vélo. Où puis-je la récupérer ?",
        ],
        "reponses": [
            "La facture de {achat} est disponible dans votre espace client, rubrique « Mes commandes » : il suffit de cliquer sur « Télécharger la facture ». Les achats en magasin y figurent aussi lorsque vous avez donné votre adresse e-mail en caisse. Si elle n'apparaît pas, répondez à ce message avec la date et le magasin d'achat, et nous vous l'enverrons.",
            "Merci pour votre message. Toutes nos factures, en ligne comme en magasin, sont téléchargeables dans votre espace client, rubrique « Mes commandes », au format PDF. Celle de {achat} s'y trouve donc. Si vous ne la voyez pas, indiquez-nous en réponse la date et le magasin d'achat : nous la rattacherons à votre compte.",
        ],
    },
    "prix_promo": {
        "categorie": "facturation",
        "priorite": "normale",
        "poids": 0.3,
        "objets": ["Code promo non appliqué", "Erreur de prix", "Réduction oubliée"],
        "messages": [
            "Bonjour,\n\nJ'ai passé la commande {cmd} avec un code de réduction mais la réduction n'a pas été appliquée, j'ai payé {montant}. Pouvez-vous corriger ?",
            "code promo pas pris en compte sur {cmd}, payé {montant}",
            "Bonjour, le prix du {article} affiché sur le site était plus bas que le montant que j'ai payé ({montant}){cmd_opt}. Il y avait une promotion. Je peux récupérer la différence ?",
        ],
        "reponses": [
            "Merci pour votre message concernant {commande}, réglée {montant}. Nous vérifions le prix appliqué et les conditions de la promotion à la date de votre achat. Si une réduction valable n'a pas été prise en compte, la différence vous sera remboursée après cette vérification, et une facture corrigée sera disponible dans votre espace client. Nous revenons vers vous par e-mail.",
            "Nous sommes désolés pour ce souci de prix sur {commande}. Notre service facturation contrôle la réduction qui aurait dû s'appliquer au montant de {montant}. Si elle était valable, l'écart vous est remboursé après vérification, et la facture corrigée apparaîtra dans votre espace client. Vous n'avez rien à faire d'ici là : nous vous écrivons dès que le contrôle est terminé.",
        ],
    },
    # compte
    "mot_de_passe": {
        "categorie": "compte",
        "priorite": "normale",
        "poids": 0.45,
        "objets": [
            "Mot de passe oublié",
            "Impossible de me connecter",
            "Connexion compte",
        ],
        "messages": [
            "Bonjour, j'ai oublié mon mot de passe et je n'arrive plus à me connecter à mon compte. Comment faire ?",
            "mdp oublié, le lien ne marche pas",
            "Bonjour,\n\nJ'ai demandé trois fois la réinitialisation de mon mot de passe mais je ne reçois aucun e-mail. J'ai vérifié les spams. Pouvez-vous m'aider ?",
            "Bonjour, je n'arrive plus à me connecter depuis la mise à jour du site, on me dit que le mot de passe est faux alors que je ne l'ai pas changé.",
        ],
        "reponses": [
            "Pour réinitialiser votre mot de passe, cliquez sur « Mot de passe oublié » sur la page de connexion et saisissez l'adresse e-mail de votre compte : vous recevrez un lien de réinitialisation. S'il n'arrive pas, vérifiez vos courriers indésirables, puis répondez à ce message avec l'adresse utilisée : nous vous enverrons un nouveau lien. Nous ne vous demanderons jamais votre mot de passe.",
            "Désolés pour ce souci de connexion. La réinitialisation se fait par lien : sur la page de connexion, choisissez « Mot de passe oublié » et indiquez l'adresse e-mail de votre compte. Si le message n'arrive pas après quelques minutes, même dans les courriers indésirables, répondez-nous en précisant cette adresse : nous vérifierons votre compte et vous renverrons un lien.",
        ],
    },
    "suppression_compte": {
        "categorie": "compte",
        "priorite": "normale",
        "poids": 0.35,
        "objets": ["Suppression de compte", "Demande RGPD", "Supprimer mes données"],
        "messages": [
            "Bonjour, je souhaite que vous supprimiez mon compte client et toutes mes données. Merci de me confirmer.",
            "supprimez mon compte svp",
            "Bonjour,\n\nConformément au RGPD, je vous demande l'effacement de mes données personnelles et la suppression de mon compte. Je ne souhaite plus recevoir de messages de votre part.",
            "Bonjour, je n'utilise plus mon compte chez vous et je reçois encore vos newsletters. Pouvez-vous fermer le compte et effacer mes informations ?",
        ],
        "reponses": [
            "Nous avons bien reçu votre demande de suppression de compte. Conformément au RGPD, votre compte et vos données personnelles seront supprimés dans un délai de 30 jours, et vous ne recevrez plus de messages de notre part. Seules les factures sont conservées, comme la loi l'exige. Un e-mail vous confirmera la suppression une fois celle-ci effectuée.",
            "Votre demande est bien prise en compte. Comme le prévoit le RGPD, nous supprimons votre compte client et les données associées dans les 30 jours ; un e-mail vous confirmera la suppression. Votre adresse est dès maintenant retirée de nos envois. Seules vos factures sont conservées, pour la durée exigée par la loi.",
        ],
    },
    "changer_email": {
        "categorie": "compte",
        "priorite": "normale",
        "poids": 0.2,
        "objets": ["Changer d'adresse e-mail", "Modifier mon e-mail"],
        "messages": [
            "Bonjour, comment changer l'adresse e-mail de mon compte ? J'ai une nouvelle adresse.",
            "Bonjour,\n\nJe n'ai plus accès à l'ancienne adresse mail liée à mon compte Biclou. Comment puis-je la modifier ?",
            "changer email compte",
        ],
        "reponses": [
            "Vous pouvez modifier l'adresse e-mail de votre compte dans votre espace client, rubrique « Mes informations ». Si vous n'avez plus accès à l'ancienne adresse, répondez à ce message en indiquant votre nom et la nouvelle adresse : nous vous enverrons un lien de confirmation pour finaliser le changement. Nous ne vous demanderons jamais votre mot de passe.",
            "Pour changer votre adresse e-mail, connectez-vous à votre espace client et ouvrez la rubrique « Mes informations ». Si la connexion est impossible, nous pouvons faire la modification pour vous : indiquez-nous en réponse la nouvelle adresse, et un lien de confirmation y sera envoyé. Le changement est effectif dès que vous cliquez sur ce lien.",
        ],
    },
}

# The English messages of the French export (4 %), for a few scenarios; the labels
# come from FR. An English version of the dataset would fill it for every scenario.
EN = {
    "horaires": {
        "objets": ["Opening hours"],
        "messages": [
            "Hi, what are the opening hours of your {ville} store? I'm visiting next week and would like to have a look at your bikes.",
            "Hello, are you open on Mondays in {ville}?",
        ],
        "reponses": [
            "Our {ville} store is open Tuesday to Saturday, from 10 am to 7 pm, and closed on Sundays and Mondays. All six of our stores keep the same hours, and you can come in without an appointment, including to test-ride a bike. Our staff will be happy to help you find the right model.",
        ],
    },
    "stock": {
        "objets": ["Is the {velo} in stock?"],
        "messages": [
            "Hello, do you have the {velo} in size {taille_cadre} in your {ville} store? I'd like to try it before buying.",
            "Is the {velo} in stock in {ville}, size {taille_cadre}?",
        ],
        "reponses": [
            "The stock of each store is shown live on the {velo} product page, under « In-store availability »: choose size {taille_cadre} and the {ville} store. If it is available, reserve it online and we will keep it for you for 3 days so you can try it. The store is open Tuesday to Saturday, from 10 am to 7 pm.",
        ],
    },
    "taille": {
        "objets": ["Which size?"],
        "messages": [
            "Hi, I'm {hauteur_en} tall. Which size of the {velo} should I get?",
            "Hello, which frame size do you recommend for the {velo}? I am {hauteur_en}.",
        ],
        "reponses": [
            "For a height of {hauteur_en}, our size guide recommends the {velo} in size {taille_cadre}. A test ride in one of our stores, Tuesday to Saturday from 10 am to 7 pm, is the best way to confirm it. If you order online and the size is not right, you can return the unused bike in its packaging within {delai_retour_en} of delivery.",
        ],
    },
    "colis_retard": {
        "objets": ["Order not received", "Delivery delay"],
        "messages": [
            "Hello, I ordered on {date_commande_en} (order {cmd}) and haven't received anything yet. Could you tell me where my parcel is?",
            "Hi, my order {cmd} still hasn't arrived. Is there a delay?",
        ],
        "reponses": [
            "We are sorry for the wait regarding {commande_en}. Our deliveries usually take 3 to 5 working days, but carriers sometimes run a few days late. If your parcel has not arrived 10 working days after shipping, simply reply to this message: we will open an investigation with the carrier, then offer you a new shipment or a refund.",
        ],
    },
    "colis_perdu": {
        "objets": ["Lost parcel?", "Order never arrived"],
        "messages": [
            "Hello, my order {cmd} from {date_commande_en} has still not arrived and the tracking hasn't moved for over two weeks. I think the parcel is lost. What can you do?",
            "Three weeks and still no parcel (order {cmd}). I want my order or my money back.",
        ],
        "reponses": [
            "We are sorry: {commande_en} should have reached you long ago. As it is more than 10 working days late, we are opening an investigation with the carrier today. Once it is closed, you will be able to choose between a new shipment and a refund. You have nothing to do in the meantime: we will email you as soon as we hear back.",
        ],
    },
    "mauvaise_taille": {
        "objets": ["Wrong size"],
        "messages": [
            "Hello, I received the {article_taille_en} in size {taille_recue} (order {cmd}) but it is too {petit_grand_en}. Can I exchange it for a {taille_voulue}?",
            "Hi, order {cmd}: the {article_taille_en} doesn't fit, I'd like to return it. It hasn't been worn.",
        ],
        "reponses": [
            "Thank you for your message about {commande_en}. You can return the {article_taille_en} within {delai_retour_en} of delivery, as long as it is unused and in its packaging. Returns are free in any of our stores, or cost €6.90 by parcel. If you bring it to a store, our staff can exchange it for the right size straight away.",
        ],
    },
    "location_tarifs": {
        "objets": ["Bike rental prices"],
        "messages": [
            "Hello, how much is it to rent an e-bike for a weekend in {ville}? Is there a deposit?",
            "Hi, what are your weekly bike rental prices in {ville}?",
        ],
        "reponses": [
            "Our {ville} store rents bikes for €15 a day or €60 a week, and e-bikes for €35 a day. A deposit of €300 (€800 for an e-bike) is taken as a card pre-authorisation in store, and is not charged. You can book online, and cancellation is free up to 24 hours before the rental starts.",
        ],
    },
    "location_accident": {
        "objets": ["Accident with a rental bike"],
        "messages": [
            "Hello, I had an accident yesterday with the bike I rented in {ville}. I'm fine but the front wheel is bent. What should I do?",
            "Hi, I fell off the rental bike from your {ville} store this morning and the derailleur is broken. How do I bring it back?",
        ],
        "reponses": [
            "We are sorry about the accident and hope you are not hurt. Please report it within 48 hours by replying to this message with the date, the place and a short description, plus photos of the bike if possible. Then bring the bike back to our {ville} store: our workshop will assess the damage before any decision on the deposit.",
        ],
    },
    "double_debit": {
        "objets": ["Charged twice"],
        "messages": [
            "Hello, I was charged twice {montant_en} for order {cmd}. Please refund the second payment.",
            "Hi, my bank shows two identical payments of {montant_en} for one purchase on your website (order {cmd}). Is this a mistake?",
        ],
        "reponses": [
            "We are sorry about this double charge of {montant_en} on {commande_en}. We are checking both payments with our payment provider today. If the duplicate is confirmed, the second charge will be refunded within 5 working days after this check, to the same payment method. There is no need to send us any bank details.",
        ],
    },
    "mot_de_passe": {
        "objets": ["Password reset"],
        "messages": [
            "Hello, I forgot my password and can't log in to my account. How can I reset it?",
            "Hi, I asked for a password reset twice but never got the email. I checked my spam folder.",
        ],
        "reponses": [
            "To reset your password, click « Forgot password » on the login page and enter the email address of your account: you will receive a reset link. If it does not arrive within a few minutes, check your spam folder, then reply to this message with the address you used and we will send you a new link.",
        ],
    },
    "freins_defaillants": {
        "objets": ["URGENT brakes"],
        "messages": [
            "Hello, the brakes on my {velo} have barely worked since this morning, I almost couldn't stop going downhill. What should I do?",
            "URGENT: the rear brake lever of my {velo} goes all the way to the handlebar, no braking at all.",
        ],
        "reponses": [
            "Thank you for warning us: failing brakes are a safety issue. Please stop riding your {velo} until it has been checked. Bring it to any of our workshops, where brake problems are handled within 48 hours, with a free diagnosis. If the fault is covered by the 2-year parts and labour warranty, the repair will cost you nothing.",
        ],
    },
    "batterie_charge": {
        "objets": ["Battery not charging"],
        "messages": [
            "Hello, the battery of my {velo_e} no longer charges, the light stays off. The bike is {age_mois} months old. What should I do?",
            "Hi, my {velo_e} battery won't charge anymore. I tried another socket and nothing.",
        ],
        "reponses": [
            "We are sorry about the battery problem on your {velo_e}. The battery is covered for 2 years or 500 charge cycles, whichever comes first. Bring the bike, battery and charger to any of our workshops: the diagnosis is free and the bike is ready within 5 working days. If the battery is out of warranty, you will get a quote before any work.",
        ],
    },
}

# The replies of the agent who breaks the charter: tutoiement, too short, no
# signature, and an immediate refund promised before any check (marked True).
BAD_REPLIES = {
    "information": [
        ("Salut ! On est ouverts du mardi au samedi, passe quand tu veux.", False),
        ("Regarde sur le site, tout y est.", False),
        (
            "Salut, oui normalement. Passe en magasin pour voir, tu pourras essayer.",
            False,
        ),
    ],
    "livraison": [
        ("Salut, ton colis arrive bientôt, t'inquiète.", False),
        ("C'est le transporteur, on n'y peut rien. Attends encore un peu.", False),
        ("Pas de souci, je te rembourse tout de suite.", True),
        ("Je t'ai remboursé, c'est fait. Bonne journée", True),
    ],
    "reparation": [
        ("Passe à l'atelier, on regardera.", False),
        ("Salut, ramène ton vélo en magasin et on verra.", False),
        ("Ça arrive, c'est rien. Passe quand tu peux.", False),
    ],
    "retour": [
        ("Ok, renvoie-le et je te rembourse direct.", True),
        ("Salut, c'est bon je t'ai remboursé.", True),
        ("Ramène-le en magasin, ils verront.", False),
    ],
    "location": [
        ("Ok c'est noté.", False),
        ("Salut, passe au magasin avec le vélo et on verra pour la caution.", False),
        ("Pas de souci, on te rembourse tout.", True),
    ],
    "facturation": [
        ("Je te rembourse tout de suite, c'est fait.", True),
        ("Ta facture est sur ton compte.", False),
        ("Salut, regarde dans ton espace client.", False),
    ],
    "compte": [
        ("Clique sur mot de passe oublié.", False),
        ("C'est fait.", False),
        ("Ok je supprime ton compte.", False),
    ],
}
UNUSABLE = [
    "",
    "voir mail",
    "Ticket fusionné avec {ticket}",
    "test",
    "cf. appel client",
    "ok",
]

# Channel artefacts.
MOBILE_SIGNATURES = {
    "fr": [
        "Envoyé de mon iPhone",
        "Envoyé depuis mon mobile",
        "Envoyé de mon smartphone",
        "--\nEnvoyé depuis l'application Courriel Plus",
    ],
    "en": ["Sent from my iPhone", "Sent from my phone"],
}
QUOTED_MAIL = {
    "fr": "Le {jour} à {heure}, Biclou & Cie <support@biclou-et-cie.example> a écrit :\n> Bonjour,\n>\n> Nous avons bien reçu votre message et vous répondrons au plus vite.\n>\n> L'équipe Biclou & Cie",
    "en": "On {jour} at {heure}, Biclou & Cie <support@biclou-et-cie.example> wrote:\n> Hello,\n>\n> We have received your message and will reply as soon as possible.\n>\n> The Biclou & Cie team",
}
# Personal data, written in the message: {email}, {tel} and {adresse} become [EMAIL],
# [TELEPHONE] and [ADRESSE] in test.jsonl.
PII_SENTENCES = {
    "email": [
        "Vous pouvez me répondre à {email}.",
        "Merci de me répondre sur {email} plutôt que sur l'adresse du compte.",
        "Mon adresse : {email}",
    ],
    "tel": [
        "Vous pouvez m'appeler au {tel}.",
        "Mon numéro : {tel}",
        "Joignable au {tel} en journée.",
    ],
    "adresse": [
        "J'habite au {adresse}.",
        "Mon adresse de livraison : {adresse}.",
    ],
}
PII_SENTENCES_EN = {
    "email": ["You can reach me at {email}."],
    "tel": ["My phone number is {tel}."],
    "adresse": ["My address is {adresse}."],
}
RELANCES = [
    "Je n'ai toujours pas eu de réponse, merci de me recontacter rapidement.",
    "Je me permets de relancer, c'est assez urgent.",
    "Toujours rien ? Merci de me répondre.",
    "PS : je vous ai déjà écrit il y a quelques jours.",
]
CAT_SPELLINGS = {
    "information": ["Information", "INFORMATION", "information ", "info"],
    "livraison": ["Livraison ", "LIVRAISON", "Livraison"],
    "reparation": ["réparation", "REPARATION", "Réparation"],
    "retour": ["Retour", "RETOUR", "retour "],
    "location": ["Location", "LOCATION", "location "],
    "facturation": ["Facturation", "FACTURATION", "facturation "],
    "compte": ["Compte", "COMPTE", "compte "],
}
PRIO_SPELLINGS = {
    "basse": ["Basse", "BASSE", "basse "],
    "normale": ["Normale", "NORMALE", "normal"],
    "haute": ["Haute", "HAUTE", "haute "],
}

FIELDNAMES = [
    "ticket_id", "date", "canal", "client", "objet", "message", "reponse", "agent",
    "statut", "satisfaction", "categorie", "priorite",
]  # fmt: skip


def slot_names(template):
    names = {name for _, name, _, _ in string.Formatter().parse(template) if name}
    return {"ville" if name == "de_ville" else name for name in names}


def check_templates():
    """A reply only uses slots every message of its scenario names."""
    for lang, bank in (("fr", FR), ("en", EN)):
        for key, scenario in bank.items():
            common = set.intersection(*(slot_names(m) for m in scenario["messages"]))
            for template in scenario["reponses"]:
                derived = DERIVED | FR[key].get("derives", set())
                missing = slot_names(template) - common - derived
                if missing:
                    raise ValueError(f"{lang}/{key}: a reply uses {missing}")


def euros(amount, lang):
    whole, cents = f"{amount:.2f}".split(".")
    if lang == "en":
        return f"€{int(whole):,}.{cents}"
    groups = f"{int(whole):,}".replace(",", " ")
    return f"{groups},{cents} €"


def french_date(day):
    return f"{'1er' if day.day == 1 else day.day} {MOIS[day.month - 1]}"


def english_date(day):
    return f"{day.day} {MONTHS[day.month - 1]}"


def frame_size(height_cm):
    if height_cm < 165:
        return "S"
    if height_cm < 175:
        return "M"
    if height_cm < 185:
        return "L"
    return "XL"


def slots(rng, scenario, day):
    """Every slot a template may use, for one ticket."""
    ville = rng.choice(VILLES)
    velo, _ = rng.choice(VELOS + VELOS_E)
    velo_e, _ = rng.choice(VELOS_E)
    accessoire, accessoire_en, _ = rng.choice(ACCESSOIRES)
    if rng.random() < 0.3:
        article, price = rng.choice(VELOS + VELOS_E)
        article_en = article
    else:
        article, article_en, price = rng.choice(ACCESSOIRES)
    article_taille, article_taille_en = rng.choice(ARTICLES_TAILLE)
    i = rng.randrange(len(TAILLES) - 1)
    trop_petit = rng.random() < 0.5
    taille_recue, taille_voulue = (
        (TAILLES[i], TAILLES[i + 1]) if trop_petit else (TAILLES[i + 1], TAILLES[i])
    )
    height = rng.randint(155, 196)
    cmd = f"CMD-{rng.randint(100000, 999999)}"
    ago = rng.randint(*scenario.get("commande_il_y_a", (8, 12)))
    old_policy = day < POLICY_CHANGE
    jours_depuis = rng.randint(18, 28) if old_policy else rng.randint(35, 55)
    jours_depuis_retour = rng.randint(16, 25)
    loc_debut = day + timedelta(days=rng.randint(3, 40))
    loc_fin = loc_debut + timedelta(days=rng.randint(1, 7))
    loc_nouveau = loc_debut + timedelta(days=rng.choice([-1, 1]) * rng.randint(2, 10))
    if loc_nouveau <= day + timedelta(days=1):
        loc_nouveau = loc_debut + timedelta(days=rng.randint(2, 10))
    evenement = day + timedelta(days=rng.randint(10, 25))
    with_cmd = rng.random() < 0.5
    return {
        "ville": ville,
        "de_ville": f"d'{ville}" if ville[0] in "AEIOU" else f"de {ville}",
        "velo": velo,
        "velo_e": velo_e,
        "accessoire": accessoire,
        "accessoire_en": accessoire_en,
        "article": article,
        "article_en": article_en,
        "article_taille": article_taille,
        "article_taille_en": article_taille_en,
        "taille_recue": taille_recue,
        "taille_voulue": taille_voulue,
        "petit_grand": "petit" if trop_petit else "grand",
        "petit_grand_en": "small" if trop_petit else "big",
        "hauteur": f"{height // 100},{height % 100:02d} m",
        "hauteur_en": f"{height // 100}.{height % 100:02d} m",
        "taille_cadre": frame_size(height),
        "cmd": cmd,
        "cmd_opt": f" (commande {cmd})" if with_cmd else "",
        "cmd_apres": f" {cmd}" if with_cmd else "",
        "montant": euros(price, "fr"),
        "montant_en": euros(price, "en"),
        "date_commande": french_date(day - timedelta(days=ago)),
        "date_commande_en": english_date(day - timedelta(days=ago)),
        "date_retour": french_date(day - timedelta(days=jours_depuis_retour)),
        "jours_depuis_retour": jours_depuis_retour,
        "jours_depuis": jours_depuis,
        "loc_debut": french_date(loc_debut),
        "loc_fin": french_date(loc_fin),
        "loc_nouveau_debut": french_date(loc_nouveau),
        "date_evenement": french_date(evenement),
        "age_mois": rng.randint(3, 20),
        "km": rng.randint(5, 18),
        "nb_velos": rng.choice(NB),
        "delai_retour": "14 jours" if old_policy else "30 jours",
        "delai_retour_en": "14 days" if old_policy else "30 days",
    }


def strip_accents(text):
    decomposed = unicodedata.normalize("NFD", text)
    kept = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", kept)


def add_typos(rng, text):
    words = text.split(" ")
    candidates = [i for i, w in enumerate(words) if len(w) > 4 and w.isalpha()]
    for i in rng.sample(candidates, min(len(candidates), rng.randint(1, 3))):
        w = words[i]
        j = rng.randrange(1, len(w) - 1)
        op = rng.choice(["swap", "drop", "double"])
        if op == "swap":
            w = w[:j] + w[j + 1] + w[j] + w[j + 2 :]
        elif op == "drop":
            w = w[:j] + w[j + 1 :]
        else:
            w = w[:j] + w[j] + w[j:]
        words[i] = w
    text = " ".join(words)
    if rng.random() < 0.5:
        text = text.replace(" ?", "?").replace(" !", "!")
    return text


def to_html(rng, text):
    if rng.random() < 0.5:
        out = "".join(
            f"<p>{p.replace(chr(10), '<br>')}</p>" for p in text.split("\n\n")
        )
    else:
        out = text.replace("\n", "<br>")
    for mark in "?!:":
        out = out.replace(f" {mark}", f"&nbsp;{mark}")
    if rng.random() < 0.3:
        out = out.replace("'", "&#39;")
    return out


def person(rng, lang):
    if lang == "en":
        gender = rng.choice("FM")
        first = rng.choice(FIRST_NAMES_F if gender == "F" else FIRST_NAMES_M)
        return gender, first, rng.choice(LAST_NAMES)
    gender = rng.choice("FM")
    first = rng.choice(PRENOMS_F if gender == "F" else PRENOMS_M)
    return gender, first, rng.choice(NOMS)


def email_of(rng, first, last):
    local = strip_accents(f"{first}.{last}").lower().replace(" ", "")
    if rng.random() < 0.3:
        local = f"{local}{rng.randint(1, 99)}"
    elif rng.random() < 0.3:
        local = strip_accents(first[0] + last).lower().replace(" ", "")
    return f"{local}@{rng.choice(DOMAINES)}"


def phone(rng):
    # The ranges ARCEP reserves for fiction: no real line answers them.
    prefix = rng.choice(["06 39 98", "01 99 00", "04 65 71", "02 61 91"])
    number = f"{prefix} {rng.randint(0, 99):02d} {rng.randint(0, 99):02d}"
    return number.replace(" ", "") if rng.random() < 0.2 else number


def signature(rng, lang, canal, gender, first, last):
    """The closing lines of a message, and the name a reply may greet."""
    signed = rng.random() < {"email": 0.85, "formulaire": 0.5, "chat": 0.12}[canal]
    closer = "" if canal == "chat" else rng.choice(CLOSERS[lang])
    known = None
    name = ""
    if signed:
        form = rng.random()
        if form < 0.6:
            name, known = f"{first} {last}", (gender, last)
        elif form < 0.75:
            name, known = f"{first} {last.upper()}", (gender, last)
        elif form < 0.9:
            if lang == "en":
                title = "Ms" if gender == "F" else "Mr"
            else:
                title = "Mme" if gender == "F" else "M."
            name, known = f"{title} {last}", (gender, last)
        else:
            name = first  # a first name only: the reply opens with "Bonjour,"
    if canal == "chat":
        return (f" {name}" if name else ""), known
    lines = [f"{closer}," if closer else "", name]
    block = "\n".join(line for line in lines if line)
    return (f"\n\n{block}" if block else ""), known


def greeting(lang, known):
    if known is None:
        return GREETINGS[lang][None]
    gender, last = known
    return GREETINGS[lang][gender].format(nom=last)


def reply(lang, known, body):
    return f"{greeting(lang, known)}\n\n{body}\n\n{SIGN_OFF[lang]}"


TUTOIEMENT = re.compile(r"\b(tu|toi|ton|ta|tes)\b|\bt'", re.IGNORECASE)


def check_reply(text, lang, message):
    """Every rule of the charter a reply can be checked against."""
    words = len(text.split())
    problems = []
    if not 40 <= words <= 120:
        problems.append(f"{words} words")
    if not text.endswith(SIGN_OFF[lang]):
        problems.append("no sign-off")
    first = text.split("\n", 1)[0]
    pattern = (
        r"Bonjour( (Madame|Monsieur) [^,]+)?,"
        if lang == "fr"
        else r"Hello( (Ms|Mr) [^,]+)?,"
    )
    if not re.fullmatch(pattern, first):
        problems.append(f"greeting {first!r}")
    if lang == "fr" and TUTOIEMENT.search(text):
        problems.append("tutoiement")
    for number in re.findall(r"CMD-\d{6}", message):
        if number not in text:
            problems.append(f"{number} not restated")
    if re.search(
        r"numéro de (votre )?carte|cryptogramme|card number", text, re.IGNORECASE
    ):
        problems.append("asks for card details")
    if problems:
        raise ValueError(f"reply breaks the charter ({', '.join(problems)}):\n{text}")
    return words


def build_ticket(rng, key, day, lang):
    """One ticket: its message as the export holds it, its masked clean version, and
    a reply that follows the charter."""
    scenario = FR[key]
    bank = EN[key] if lang == "en" else scenario
    noise = []
    s = slots(rng, scenario, day)
    canal = rng.choices(["email", "formulaire", "chat"], [0.45, 0.30, 0.25])[0]
    hour, minute = rng.randint(7, 22), rng.randrange(60)
    if canal == "chat":
        if day.weekday() in (0, 6):  # the chat follows the stores' opening days
            canal = "email"
        else:
            hour = rng.randint(10, 18)
    template_index = rng.randrange(len(bank["messages"]))
    body = bank["messages"][template_index].format_map(s)
    if lang == "fr" and body.startswith("Bonjour,\n\n"):
        hello = "Bonsoir," if hour >= 18 else "Bonjour,"
        opener = rng.choice([hello, hello, "Madame, Monsieur,", "Bonjour à vous,"])
        body = opener + body[len("Bonjour,") :]
    elif lang == "fr" and body.startswith("Bonjour, "):
        hello = "Bonsoir, " if hour >= 18 else "Bonjour, "
        opener = rng.choice([hello, hello, "Bonjour ", "Bjr, ", ""])
        body = opener + body[len("Bonjour, ") :]
        body = body[0].upper() + body[1:]
    if lang == "fr":
        roll = rng.random()
        if roll < RATES["shouting"]:
            body = body.upper()
            noise.append("message: all caps")
        elif roll < RATES["shouting"] + RATES["no_accents"]:
            body = strip_accents(body)
            noise.append("message: no accents")
        if rng.random() < RATES["typos"]:
            body = add_typos(rng, body)
            noise.append("message: typos")

    gender, first, last = person(rng, lang)
    client = f"{first} {last}"
    sign, known = signature(rng, lang, canal, gender, first, last)

    # Personal data, written in two versions: the export's and the masked one.
    pii = {}
    sentences = PII_SENTENCES_EN if lang == "en" else PII_SENTENCES
    extra_real, extra_masked = [], []
    if rng.random() < RATES["email"]:
        pii["email"] = email_of(rng, first, last)
    if rng.random() < RATES["phone"]:
        pii["tel"] = phone(rng)
    wants_address = key == "changer_adresse" and rng.random() < 0.35
    if wants_address or rng.random() < RATES["address"]:
        ville = rng.choice(VILLES)
        pii["adresse"] = (
            f"{rng.randint(1, 120)} {rng.choice(RUES)}, {CODES_POSTAUX[ville]} {ville}"
        )
    masks = {"email": "[EMAIL]", "tel": "[TELEPHONE]", "adresse": "[ADRESSE]"}
    for kind, value in pii.items():
        noise.append(f"message: {kind}")
        sentence = rng.choice(sentences[kind])
        extra_real.append(sentence.format(**{kind: value}))
        extra_masked.append(sentence.format(**{kind: masks[kind]}))
    sep = " " if canal == "chat" else "\n\n"
    real = body + "".join(sep + e for e in extra_real) + sign
    masked = body + "".join(sep + e for e in extra_masked) + sign

    # Channel artefacts: in the export only.
    message = real
    if canal == "email" and rng.random() < RATES["mobile_signature"]:
        message += "\n\n" + rng.choice(MOBILE_SIGNATURES[lang])
        noise.append("message: mobile signature")
    if canal == "email" and rng.random() < RATES["quoted_mail"]:
        before = day - timedelta(days=rng.randint(1, 6))
        jour = (
            french_date(before) + f" {before.year}"
            if lang == "fr"
            else english_date(before) + f" {before.year}"
        )
        heure = f"{rng.randint(8, 19):02d}:{rng.randrange(60):02d}"
        message += "\n\n" + QUOTED_MAIL[lang].format(jour=jour, heure=heure)
        noise.append("message: quoted mail")
    if canal == "formulaire" and rng.random() < RATES["html"]:
        message = to_html(rng, message)
        noise.append("message: HTML")

    # Derived slots: the order number the message gives.
    given = s["cmd"] in body
    s["commande"] = f"votre commande {s['cmd']}" if given else "votre commande"
    s["achat"] = f"votre commande {s['cmd']}" if given else "votre achat"
    s["commande_en"] = f"your order {s['cmd']}" if given else "your order"
    reply_index = rng.randrange(len(bank["reponses"]))
    text = reply(lang, known, bank["reponses"][reply_index].format_map(s))
    check_reply(text, lang, body)

    if lang == "fr" and canal == "formulaire":
        objet = (
            FORM_SUBJECTS[scenario["categorie"]] if rng.random() > 0.1 else FORM_OTHER
        )
    elif canal == "chat":
        objet = CHAT_SUBJECT[lang]
    else:
        objet = rng.choice(bank["objets"]).format_map(s)

    return {
        "date": datetime(day.year, day.month, day.day, hour, minute),
        "canal": canal,
        "client": client,
        "objet": objet,
        "message": message,
        "reponse": text,
        "agent": rng.choice(ENGLISH_AGENTS if lang == "en" else AGENTS),
        "statut": "resolu",
        "categorie": scenario["categorie"],
        "priorite": scenario["priorite"],
        # Kept for the noise and the test set, not written to the CSV.
        "_key": key,
        "_lang": lang,
        "_slots": s,
        "_known": known,
        "_masked": masked,
        "_body": body,
        "_reply_index": reply_index,
        "_old_policy": day < POLICY_CHANGE
        and "{delai_retour" in bank["reponses"][reply_index],
        "_kind": "base",
        "_noise": noise,
    }


def draw_days(rng, category, n):
    days = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    season = SEASONS.get(category, SEASONS["default"])
    total = len(days)
    weights = [season[d.month - 1] * (1 + 0.3 * i / total) for i, d in enumerate(days)]
    return rng.choices(days, weights, k=n)


def base_tickets(rng):
    tickets = []
    for category, share in CATEGORIES.items():
        n = round(N_BASE * share)
        keys = [k for k, sc in FR.items() if sc["categorie"] == category]
        weights = [FR[k]["poids"] for k in keys]
        for day in draw_days(rng, category, n):
            key = rng.choices(keys, weights)[0]
            lang = "en" if key in EN and rng.random() < RATES["english"] else "fr"
            tickets.append(build_ticket(rng, key, day, lang))
    return tickets


def near_duplicates(rng, tickets):
    """Customers who send the same message again, a few hours or days later."""
    resent = []
    for original in rng.sample(tickets, round(RATES["near_duplicate"] * len(tickets))):
        copy = dict(original)
        copy["date"] = original["date"] + timedelta(
            hours=rng.randint(3, 96), minutes=rng.randrange(60)
        )
        if copy["date"].date() > END:
            copy["date"] = original["date"] + timedelta(hours=rng.randint(1, 5))
        if copy["canal"] == "chat":  # a new chat, on a later opening day
            later = original["date"].date() + timedelta(days=rng.randint(1, 3))
            while later.weekday() in (0, 6):
                later += timedelta(days=1)
            if later > END:
                later = original["date"].date()
            hour = (
                max(original["date"].hour + 1, 10)
                if later == original["date"].date()
                else 10
            )
            copy["date"] = datetime(
                later.year,
                later.month,
                later.day,
                rng.randint(hour, 18),
                rng.randrange(60),
            )
        if original["_lang"] == "fr" and rng.random() < 0.5:
            copy["message"] = "Relance : " + original["message"]
        else:
            extra = (
                RELANCES[rng.randrange(len(RELANCES))]
                if original["_lang"] == "fr"
                else "Still no answer, please get back to me."
            )
            copy["message"] = original["message"] + "\n\n" + extra
        if copy["canal"] == "email":
            copy["objet"] = (
                "Relance : " if original["_lang"] == "fr" else "Reminder: "
            ) + original["objet"]
        copy["_kind"] = "near_duplicate"
        noise = copy["_noise"] = [*original["_noise"], "near duplicate"]
        copy["_original"] = original
        if rng.random() < 0.5:
            copy["reponse"] = "Ticket fusionné avec {ticket}"
            copy["statut"] = "fusionne"
            copy["_old_policy"] = False
            noise.append("near duplicate: merged")
        else:
            noise.append("near duplicate: answered again")
        resent.append(copy)
    return resent


def degrade(rng, tickets):
    """Unusable replies, open tickets, the agent who breaks the charter."""
    for t in tickets:
        if t["_kind"] != "base":
            continue
        roll = rng.random()
        if roll < RATES["open"]:
            t["_kind"] = "open"
        elif roll < RATES["open"] + RATES["unusable"]:
            t["_kind"] = "unusable"
        elif (
            t["_lang"] == "fr"
            and roll < RATES["open"] + RATES["unusable"] + RATES["bad_agent"]
        ):
            t["_kind"] = "bad_agent"
    # The tickets still open are mostly the latest ones.
    recent = [
        t
        for t in tickets
        if t["_kind"] == "base" and t["date"].date() >= END - timedelta(days=45)
    ]
    for t in rng.sample(recent, min(len(recent), 30)):
        t["_kind"] = "open"
    for t in tickets:
        noise = t["_noise"]
        if t["_kind"] == "open":
            t["reponse"] = ""
            t["statut"] = "ouvert"
            t["_old_policy"] = False
            if rng.random() < 0.5:
                t["agent"] = ""
            noise.append("open, no reply")
        elif t["_kind"] == "unusable":
            t["reponse"] = rng.choice(UNUSABLE)
            t["_old_policy"] = False
            if t["reponse"].startswith("Ticket fusionné"):
                t["statut"] = "fusionne"
            elif t["reponse"] == "" and rng.random() < 0.5:
                t["statut"] = "ouvert"
            label = t["reponse"].split(" avec ")[0] or "(empty)"
            noise.append(f"unusable reply: {label}")
        elif t["_kind"] == "bad_agent":
            text, refund = rng.choice(BAD_REPLIES[t["categorie"]])
            if rng.random() < 0.3:
                text += f"\n{BAD_AGENT}"
            t["reponse"] = text
            t["agent"] = BAD_AGENT
            t["_old_policy"] = False
            noise.append("bad agent reply")
            if refund:
                noise.append("bad agent: refund promised")


def satisfaction(rng, t):
    if t["statut"] != "resolu" or rng.random() < RATES["satisfaction_empty"]:
        return ""
    if t["agent"] == BAD_AGENT:
        weights = [45, 33, 15, 5, 2]
    elif t["_kind"] == "unusable":
        weights = [20, 20, 30, 20, 10]
    elif FR[t["_key"]]["priorite"] == "haute":
        weights = [8, 10, 20, 32, 30]
    else:
        weights = [3, 4, 12, 36, 45]
    return str(rng.choices([1, 2, 3, 4, 5], weights)[0])


def messy_labels(rng, row):
    noise = row["_labels"] = []
    roll = rng.random()
    if roll < RATES["label_empty"]:
        which = rng.choice(["categorie", "priorite", "both"])
        if which in ("categorie", "both"):
            row["categorie"] = ""
        if which in ("priorite", "both"):
            row["priorite"] = ""
        noise.append(f"label empty: {which}")
    elif roll < RATES["label_empty"] + RATES["label_spelling"]:
        if rng.random() < 0.6:
            row["categorie"] = rng.choice(CAT_SPELLINGS[row["categorie"]])
            noise.append("label spelling: categorie")
        else:
            row["priorite"] = rng.choice(PRIO_SPELLINGS[row["priorite"]])
            noise.append("label spelling: priorite")


def test_examples(rng, tickets):
    """150 examples of 2026 the support team validated, with a reply that follows the
    current charter, whatever the original reply was."""
    examples = []
    for category, quota in TEST_QUOTAS.items():
        pool = [
            t
            for t in tickets
            if t["_kind"] != "near_duplicate"
            and t["_lang"] == "fr"
            and t["categorie_vraie"] == category
            and t["date"].date() >= TEST_FROM
        ]
        for t in rng.sample(pool, quota):
            replies = FR[t["_key"]]["reponses"]
            others = [i for i in range(len(replies)) if i != t["_reply_index"]] or [0]
            body = replies[rng.choice(others)].format_map(t["_slots"])
            text = reply("fr", t["_known"], body)
            check_reply(text, "fr", t["_body"])
            examples.append({
                "ticket_id": t["ticket_id"],
                "message": t["_masked"],
                "categorie": category,
                "priorite": FR[t["_key"]]["priorite"],
                "reponse": text,
            })  # fmt: skip
    examples.sort(key=lambda e: e["ticket_id"])
    return examples


def main():
    check_templates()
    rng = random.Random(SEED)
    counts = Counter()
    tickets = base_tickets(rng)
    for t in tickets:
        t["categorie_vraie"] = t["categorie"]
    resent = near_duplicates(rng, tickets)
    for t in resent:
        t["categorie_vraie"] = t["categorie"]
    tickets += resent
    degrade(rng, tickets)
    tickets.sort(key=lambda t: t["date"])
    number = 10000
    for t in tickets:
        number += rng.randint(1, 3)
        t["ticket_id"] = f"T-{number}"
    for t in tickets:
        if "{ticket}" in t["reponse"]:
            target = t.get("_original")
            if target is None:  # an agent merged it with an earlier ticket
                earlier = [u for u in tickets if u["date"] < t["date"]][-20:]
                target = rng.choice(earlier) if earlier else t
            t["reponse"] = t["reponse"].format(ticket=target["ticket_id"])

    rows = []
    for t in tickets:
        row = {name: t.get(name, "") for name in FIELDNAMES}
        row["date"] = t["date"].strftime("%Y-%m-%dT%H:%M")
        row["satisfaction"] = satisfaction(rng, t)
        messy_labels(rng, row)
        row["_t"] = t
        rows.append(row)

    # The export ran twice on some days: those days' rows appear twice.
    by_day = {}
    for row in rows:
        by_day.setdefault(row["date"][:10], []).append(row)
    target = round(
        RATES["exact_duplicate"] * len(rows) / (1 - RATES["exact_duplicate"])
    )
    doubled = set()
    for day in rng.sample(sorted(by_day), len(by_day)):
        if counts["exact duplicate rows"] >= target:
            break
        doubled.add(day)
        counts["exact duplicate rows"] += len(by_day[day])
        counts["days exported twice"] += 1
    final = []
    for day in sorted(by_day):
        final += by_day[day]
        if day in doubled:
            final += by_day[day]

    examples = test_examples(rng, tickets)

    with (HERE / "tickets.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(final)
    with (HERE / "test.jsonl").open("w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    # Counts, over every row of the export.
    final_tickets = [row["_t"] for row in final]
    counts.update(
        flag for row in final for flag in row["_t"]["_noise"] + row["_labels"]
    )
    counts["message: email or phone"] = sum(
        any(f in ("message: email", "message: tel") for f in t["_noise"])
        for t in final_tickets
    )
    counts["english messages"] = sum(t["_lang"] == "en" for t in final_tickets)
    counts["replies with the 14-day return window"] = sum(
        t["_old_policy"] for t in final_tickets
    )
    counts["satisfaction empty"] = sum(row["satisfaction"] == "" for row in final)
    counts["satisfaction 1-2, bad agent"] = sum(
        row["satisfaction"] in ("1", "2") and row["agent"] == BAD_AGENT for row in final
    )
    counts["satisfaction 1-2, other agents"] = sum(
        row["satisfaction"] in ("1", "2") and row["agent"] != BAD_AGENT for row in final
    )
    print(f"rows: {len(final)} ({len(tickets)} tickets, {len(resent)} of them re-sent)")
    print(
        "categories:",
        dict(Counter(t["categorie_vraie"] for t in final_tickets).most_common()),
    )
    print(
        "priorities:",
        dict(Counter(FR[t["_key"]]["priorite"] for t in final_tickets).most_common()),
    )
    print("canaux:", dict(Counter(row["canal"] for row in final).most_common()))
    print("statuts:", dict(Counter(row["statut"] for row in final).most_common()))
    print("agents:", dict(Counter(row["agent"] for row in final).most_common()))
    for name, value in sorted(counts.items()):
        print(f"  {name}: {value} ({value / len(final):.1%} of the rows)")
    print("test:", len(examples), dict(Counter(e["categorie"] for e in examples)))


if __name__ == "__main__":
    main()
