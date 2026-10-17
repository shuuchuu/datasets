"""Write synthetic Bluesky-like posts about Ikea, in French and English.

Every post is written from the templates below (no real post is used), with the noise
a real search returns: links, masked mentions, hashtags, emojis, posts in another
language, posts with no words, and a bot posting the same promotion several times.
Dates span 2026-08-20 to 2026-10-17, with three peaks: the autumn collection
(2026-09-10), a website outage (2026-09-25) and a sales weekend (2026-10-03/04).

`python generate.py` (standard library only) rewrites posts-fr.csv and posts-en.csv;
the seed makes it reproducible.
"""

import csv
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

SEED = 2026
START = datetime(2026, 8, 20, tzinfo=UTC)
DAYS = 59
PEAKS = {  # day: (topic, number of extra posts)
  "2026-09-10": ("collection", 28),
  "2026-09-25": ("outage", 32),
  "2026-10-03": ("sales", 22),
  "2026-10-04": ("sales", 14),
}
BASE_PER_DAY = (3, 7)

PRODUCTS = ["Billy", "Kallax", "Malm", "Pax", "Hemnes", "Poäng", "Lack", "Besta"]

FR = {
  "assembly": [
    "Trois heures pour monter une armoire {p}. Il me reste quatre vis et je ne sais pas d'où elles sortent {e}",
    "Montage du lit {p} terminé ! La notice Ikea reste un mystère mais on y est arrivés {e}",
    "Quelqu'un a déjà monté un {p} seul ? Je suis à l'étape 12 et je doute de tout",
    "La notice de montage sans un seul mot, c'est quand même génial. Sauf l'étape 7. #ikea",
    "Il manque une vis dans le carton du {p}. Retour au magasin demain {e}",
    "Monter des meubles Ikea en couple, le vrai test de solidité {e} #montage",
    "Mon {p} est monté de travers mais il tient. C'est l'essentiel.",
    "Petit conseil : visseuse électrique et patience pour le montage du {p}.",
  ],
  "delivery": [
    "Livraison Ikea annoncée entre 8 h et 18 h, toujours rien à 19 h {e}",
    "Commande passée il y a trois semaines, la livraison du {p} est encore repoussée",
    "Livraison rapide et livreurs adorables, le {p} est arrivé en parfait état {e}",
    "Le colis du {p} est arrivé abîmé, un panneau fendu. On verra ce que dit le SAV",
    "Retrait en magasin bien plus rapide que la livraison, je recommande #ikea",
    "Deuxième créneau de livraison raté, je commence à perdre patience @anonyme",
  ],
  "service": [
    "Service client Ikea au téléphone : 45 minutes d'attente pour un remboursement {e}",
    "Le SAV m'a renvoyé les pièces manquantes en deux jours, rien à dire {e}",
    "Remboursement du {p} toujours pas reçu après un mois. Quelqu'un a eu le même souci ?",
    "@anonyme le service client a été vraiment sympa avec mon retour, merci",
    "Échange sans ticket refusé, alors que le meuble n'a jamais été déballé {e}",
    "Le chat du service client répond vite, et le problème est réglé #ikea",
  ],
  "price": [
    "Le {p} a pris 20 € en un an, ça pique {e}",
    "Les prix Ikea ont bien augmenté, le meuble pas cher c'est fini ?",
    "Toujours imbattable pour meubler un premier appartement avec un petit budget",
    "Comparé aux autres enseignes, le {p} reste le meilleur rapport qualité-prix",
    "Quand tu viens pour une ampoule et que tu repars avec 200 € de déco {e}",
  ],
  "restaurant": [
    "Les boulettes du restaurant Ikea, la vraie raison d'y aller {e}",
    "Hot-dog à 1 € à la sortie des caisses, le meilleur moment de la journée",
    "Restaurant Ikea bondé ce midi, une demi-heure de queue pour des boulettes {e}",
    "Les boulettes végétales sont meilleures que les classiques, je persiste #ikea",
  ],
  "sustainability": [
    "Ikea rachète les meubles d'occasion, j'ai revendu mon vieux {p} pour un bon d'achat",
    "Le coin seconde main du magasin est une mine d'or {e} #secondemain",
    "D'où vient le bois des meubles Ikea ? Les forêts certifiées, vraiment ? #durable",
    "Bonne idée les pièces détachées gratuites, ça évite de jeter un meuble entier",
    "Meubles en panneaux de particules = durée de vie courte. Pas très durable tout ça.",
  ],
  "product": [
    "Le {p} est vraiment le meuble à tout faire, j'en ai dans chaque pièce {e}",
    "Mon fauteuil Poäng a dix ans et il est toujours parfait",
    "Le requin en peluche Blåhaj a pris le contrôle du canapé {e}",
    "Une étagère {p} pleine de plantes, le salon a changé de tête #déco",
    "Le Kallax, c'est le meilleur rangement pour les vinyles, pas de débat",
    "Cuisine Ikea installée depuis cinq ans, aucune porte n'a bougé",
  ],
  "store": [
    "Le parcours fléché du magasin, impossible d'en sortir en moins de deux heures {e}",
    "Samedi après-midi chez Ikea, mauvaise idée, le parking est plein",
    "Le magasin a encore changé l'emplacement des rayons, je suis perdu {e}",
    "Petit tour chez Ikea pour une lampe, j'ai fait tout le parcours quand même",
  ],
  "collection": [
    "Les vases de la nouvelle collection Ikea sont déjà partout sur mon fil {e}",
    "Nouvelle collection : enfin des coussins qui ne sont pas gris",
    "Le tapis de la collection d'automne est magnifique mais trop cher pour moi",
    "Collection automne Ikea : bougies, plaids, lampes, mon portefeuille tremble {e}",
    "La nouvelle collection d'automne Ikea est sortie, les couleurs sont superbes {e}",
    "Nouvelle collection Ikea : les lampes en papier sont déjà en rupture",
    "Vu la nouvelle collection automne, le plaid côtelé me fait de l'œil {e} #déco",
    "Collection d'automne Ikea un peu décevante, beaucoup de beige",
    "Je veux tout dans la nouvelle collection, surtout le canapé vert {e}",
  ],
  "outage": [
    "Impossible de me connecter à mon compte Ikea, le site affiche une erreur {e}",
    "Commande du {p} bloquée au paiement, le site Ikea rame depuis midi",
    "Le site Ikea est revenu ? Mon panier a disparu {e}",
    "Trois essais pour payer sur le site Ikea, trois erreurs. Panne générale ?",
    "L'appli Ikea me déconnecte toutes les deux minutes {e}",
    "Le site Ikea ne marche plus, impossible de valider ma commande {e}",
    "Appli Ikea en panne depuis ce matin, panier perdu deux fois",
    "Panne du site Ikea : erreur au paiement, quelqu'un d'autre ? @anonyme",
    "Le site Ikea plante au moment de payer, j'abandonne pour aujourd'hui {e}",
    "Toujours en panne le site, et le service client est injoignable",
  ],
  "sales": [
    "Les promos Ikea sur la literie valent le détour, matelas à moitié prix {e}",
    "Rayon promo dévalisé avant midi, il ne reste plus un {p}",
    "J'ai attendu les soldes pour le {p}, bonne pioche",
    "Promos du week-end : la file d'attente du parking commence sur la rocade {e}",
    "Soldes Ikea ce week-end : -30 % sur le {p}, j'ai craqué {e}",
    "Le magasin est pris d'assaut pour les promos, une heure aux caisses",
    "Promo sur les rangements, j'ai enfin pris le {p} que je voulais",
    "Les promos du week-end ne valent pas la foule {e}",
  ],
}

EN = {
  "assembly": [
    "Three hours to build a {p} wardrobe. Four screws left over and I have no idea where they belong {e}",
    "{p} bed finally assembled! The Ikea manual is still a mystery but we made it {e}",
    "Has anyone ever built a {p} alone? I'm on step 12 and I doubt everything",
    "Assembly instructions without a single word are genius. Except step 7. #ikea",
    "One screw missing from the {p} box. Back to the store tomorrow {e}",
    "Building Ikea furniture as a couple, the real relationship test {e} #flatpack",
    "My {p} is slightly crooked but it holds. That's what counts.",
    "Quick tip: power drill and patience for the {p} assembly.",
  ],
  "delivery": [
    "Ikea delivery window 8am to 6pm, still nothing at 7pm {e}",
    "Ordered three weeks ago, the {p} delivery has been pushed back again",
    "Fast delivery and lovely drivers, the {p} arrived in perfect shape {e}",
    "The {p} box arrived damaged, one panel cracked. Let's see what customer service says",
    "Click and collect is way faster than delivery, recommend #ikea",
    "Second missed delivery slot, I'm running out of patience @anonymous",
  ],
  "service": [
    "Ikea customer service on the phone: 45 minutes on hold for a refund {e}",
    "Customer service sent the missing parts in two days, no complaints {e}",
    "Still no refund for the {p} after a month. Anyone else had this problem?",
    "@anonymous customer service was really kind about my return, thanks",
    "Exchange refused without a receipt, and the box was never opened {e}",
    "The customer service chat answers fast and the problem is solved #ikea",
  ],
  "price": [
    "The {p} went up $20 in a year, ouch {e}",
    "Ikea prices really went up, is cheap furniture over?",
    "Still unbeatable to furnish a first apartment on a small budget",
    "Compared to other stores, the {p} is still the best value for money",
    "When you go in for a light bulb and leave with $200 of decor {e}",
  ],
  "restaurant": [
    "Ikea meatballs, the real reason to go {e}",
    "The $1 hot dog after the checkout, best part of the day",
    "Ikea restaurant packed at lunch, half an hour in line for meatballs {e}",
    "The plant balls are better than the classic meatballs, I stand by it #ikea",
  ],
  "sustainability": [
    "Ikea buys back used furniture, I sold my old {p} for store credit",
    "The store's second-hand corner is a gold mine {e} #secondhand",
    "Where does Ikea's wood come from? Certified forests, really? #sustainability",
    "Free spare parts are a good idea, no need to throw away a whole piece",
    "Particle board furniture = short life. Not very sustainable.",
  ],
  "product": [
    "The {p} really is the do-it-all furniture, I have one in every room {e}",
    "My Poäng chair is ten years old and still perfect",
    "The Blåhaj shark plush has taken over the couch {e}",
    "A {p} shelf full of plants, the living room looks brand new #homedecor",
    "The Kallax is the best storage for vinyl records, no debate",
    "Ikea kitchen installed five years ago, not a single door has moved",
  ],
  "store": [
    "The store's one-way maze, impossible to get out in less than two hours {e}",
    "Saturday afternoon at Ikea, bad idea, the parking lot is full",
    "The store moved the aisles again, I'm lost {e}",
    "Quick trip to Ikea for a lamp, still walked the whole showroom",
  ],
  "collection": [
    "The vases from the new Ikea collection are all over my feed {e}",
    "New collection: finally cushions that aren't grey",
    "The rug from the autumn collection is beautiful but too pricey for me",
    "Ikea autumn collection: candles, throws, lamps, my wallet is shaking {e}",
    "The new Ikea autumn collection is out, the colors are gorgeous {e}",
    "New Ikea collection: the paper lamps are already sold out",
    "Saw the new autumn collection, the ribbed throw is calling me {e} #homedecor",
    "Ikea autumn collection a bit disappointing, a lot of beige",
    "I want everything in the new collection, especially the green sofa {e}",
  ],
  "outage": [
    "Can't log in to my Ikea account, the site shows an error {e}",
    "My {p} order is stuck at payment, the Ikea site has been crawling since noon",
    "Is the Ikea site back? My cart is gone {e}",
    "Three tries to pay on the Ikea site, three errors. Global outage?",
    "The Ikea app logs me out every two minutes {e}",
    "The Ikea website is down, can't complete my order {e}",
    "Ikea app down since this morning, lost my cart twice",
    "Ikea website outage: payment error, anyone else? @anonymous",
    "The Ikea site crashes at checkout, giving up for today {e}",
    "Website still down, and customer service can't be reached",
  ],
  "sales": [
    "Ikea's mattress deals are worth it, half price {e}",
    "Sale section cleaned out before noon, not a single {p} left",
    "Waited for the sale to get the {p}, good call",
    "Weekend sale: the parking line starts on the highway {e}",
    "Ikea sale this weekend: 30% off the {p}, couldn't resist {e}",
    "The store is packed for the sale, an hour at the checkout",
    "Storage on sale, I finally got the {p} I wanted",
    "The weekend deals aren't worth the crowds {e}",
  ],
}

# Noise.
EMOJIS = ["😅", "😂", "🙃", "😍", "🤯", "😤", "🛋️", "🔧", "📦", "👍", "🙄", "💸", "🦈", "✨"]
HASHTAGS = {"fr": ["#ikea", "#déco", "#maison", "#DIY", "#meuble"], "en": ["#ikea", "#homedecor", "#DIY", "#furniture", "#home"]}
LINKS = {
  "fr": ["ikea.com/fr/fr/p/{slug}/", "https://www.ikea.com/fr/fr/campaigns/", "blog-deco.example/billets/{slug}", "https://bit.ly/3xK{n}"],
  "en": ["ikea.com/us/en/p/{slug}/", "https://www.ikea.com/us/en/campaigns/", "homeblog.example/posts/{slug}", "https://bit.ly/3xK{n}"],
}
LINK_INTRO = {"fr": ["Je partage :", "À lire :", "Mon article :", ""], "en": ["Sharing:", "Worth a read:", "My post:", ""]}
OTHER_LANGUAGE = {  # posts a search in one language returns in the other
  "fr": EN,
  "en": FR,
}
BOT = {
  "fr": "🔥 PROMO 🔥 Meubles Ikea jusqu'à -50 % ! Liste des bons plans ici 👉 https://bit.ly/3xKpromo #ikea #bonplan",
  "en": "🔥 DEAL 🔥 Ikea furniture up to 50% off! Full list of deals here 👉 https://bit.ly/3xKdeal #ikea #deals",
}
OPENERS = {
  "fr": ["Franchement,", "Honnêtement,", "Bon.", "Sérieusement,", "Alors voilà :", "Mise à jour :", "Ce matin :", "Hier soir :", "Petit retour :", "Anecdote :", "Pour info,", "Bref,", "Au fait,", "Dites,", "Ok,", "Bon courage à moi.", "Évidemment,", "Pff.", "Ah oui,", "Vraiment,"],
  "en": ["Honestly,", "Okay so", "Real talk:", "Story time:", "Seriously,", "Update:", "Not gonna lie,", "This morning:", "PSA:", "Last night:", "Quick note:", "Fun fact:", "So,", "Well,", "Ugh.", "Of course,", "Funny thing,", "Heads up:", "Oh,", "Wow."],
}
CLOSERS = {
  "fr": ["On en reparle.", "Je vous tiens au courant.", "Avis aux amateurs.", "Voilà voilà.", "À suivre.", "Fin du fil.", "Vos avis ?", "Ça promet.", "Courage.", "Tant pis.", "On verra.", "Ça arrive.", "C'est noté.", "Classique.", "Bonne soirée.", "Sans commentaire.", "Merci qui ?", "Encore.", "Enfin.", "Ouf."],
  "en": ["Will report back.", "Anyway.", "Just saying.", "More soon.", "That's all.", "To be continued.", "Thoughts?", "Carry on.", "Classic.", "Oh well.", "We'll see.", "Noted.", "Phew.", "Typical.", "Good night.", "No comment.", "Again.", "Finally.", "Sigh.", "Yep."],
}
CONTEXTS = {  # where it happened: a store, or the room of a home
  "fr": {
    "store": ["Lyon", "Lille", "Nantes", "Bordeaux", "Rennes", "Toulouse", "Marseille", "Strasbourg", "Montpellier", "Grenoble", "Rouen"],
    "home": ["nouvel appart", "chambre des enfants", "bureau à la maison", "studio étudiant", "maison de campagne", "colocation", "premier appartement", "déménagement en cours", "salle de bain", "grenier aménagé", "chambre d'amis"],
  },
  "en": {
    "store": ["Chicago", "Brooklyn", "Seattle", "Atlanta", "Houston", "Denver", "Leeds", "Manchester", "Dublin", "Toronto", "Sydney"],
    "home": ["new apartment", "kids' room", "home office", "student dorm", "cabin", "shared flat", "first apartment", "moving week", "bathroom", "attic conversion", "spare room"],
  },
}
WHERE = {"assembly": "home", "delivery": "home", "service": "store", "price": "store", "restaurant": "store", "sustainability": "store", "store": "store", "collection": "store", "sales": "store"}
WORDLESS = ["{e}{e}{e}", "{link} {e}", "📦➡️🛋️ {link}", "{e} #ikea"]
TOPICS = ["assembly", "delivery", "service", "price", "restaurant", "sustainability", "product", "store"]
WEIGHTS = [5, 3, 3, 3, 2, 2, 4, 2]


def fill(rng, template, lang, topic):
  slug = rng.choice(PRODUCTS).lower().replace("ä", "a") + f"-{rng.randint(10, 99)}"
  link = rng.choice(LINKS[lang]).format(slug=slug, n=rng.randint(100, 999))
  text = template.format(p=rng.choice(PRODUCTS), e=rng.choice(EMOJIS), link=link)
  if topic in WHERE and rng.random() < 0.5:
    text = f"{text} ({rng.choice(CONTEXTS[lang][WHERE[topic]])})"
  if rng.random() < 0.3:
    first = text.split()[0].strip(",:!?'s")
    opener = rng.choice(OPENERS[lang])
    # proper nouns, and the start of a new sentence, keep their capital
    keep = first in {"Ikea", "Blåhaj", "I", *PRODUCTS} or opener.endswith(".")
    text = f"{opener} {text if keep else text[0].lower() + text[1:]}"
  if rng.random() < 0.3 and not text.split()[-1].startswith("#"):
    end = "" if not text[-1].isalnum() else "."
    text = f"{text}{end} {rng.choice(CLOSERS[lang])}"
  if rng.random() < 0.15:  # a link after the text
    text = f"{text} {rng.choice(LINK_INTRO[lang])} {link}".replace("  ", " ")
  hashtag = rng.choice(HASHTAGS[lang])
  if rng.random() < 0.2 and hashtag not in text:
    text = f"{text} {hashtag}"
  if rng.random() < 0.05:
    text = text.replace("Ikea", "IKEA") if rng.random() < 0.5 else text.replace("Ikea", "Ikéa")
  if rng.random() < 0.08:
    text = f"@anonyme {text}" if lang == "fr" else f"@anonymous {text}"
  return text


def posts_for(lang):
  rng = random.Random(f"{SEED}-{lang}")
  bank = FR if lang == "fr" else EN
  rows = []

  def add(day, text, boost=1.0):
    moment = day + timedelta(seconds=rng.randint(7 * 3600, 23 * 3600), milliseconds=rng.randint(0, 999))
    likes = int(rng.paretovariate(1.3) * boost) - 1
    rows.append({
      "post_id": f"{rng.getrandbits(64):016x}",
      "created_at": moment.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
      "text": text,
      "likes": likes,
      "reposts": int(likes * rng.random() * 0.3),
      "replies": int(likes * rng.random() * 0.4),
    })

  for d in range(DAYS):
    day = START + timedelta(days=d)
    for _ in range(rng.randint(*BASE_PER_DAY)):
      roll = rng.random()
      if roll < 0.08:  # a post in the other language
        other = "en" if lang == "fr" else "fr"
        topic = rng.choices(TOPICS, WEIGHTS)[0]
        add(day, fill(rng, rng.choice(OTHER_LANGUAGE[lang][topic]), other, topic))
      elif roll < 0.12:  # no word left after cleaning
        link = rng.choice(LINKS[lang]).format(slug="kallax-42", n=rng.randint(100, 999))
        add(day, rng.choice(WORDLESS).format(e=rng.choice(EMOJIS), link=link))
      else:
        topic = rng.choices(TOPICS, WEIGHTS)[0]
        add(day, fill(rng, rng.choice(bank[topic]), lang, topic))
    if d % 9 == 4:  # the deals bot, several times the same day
      for _ in range(rng.randint(2, 4)):
        add(day, BOT[lang])
    key = day.strftime("%Y-%m-%d")
    if key in PEAKS:
      topic, extra = PEAKS[key]
      for _ in range(extra):
        add(day, fill(rng, rng.choice(bank[topic]), lang, topic), boost=3.0)
  rows.sort(key=lambda row: row["created_at"], reverse=True)
  return rows


def main():
  here = Path(__file__).parent
  for lang in ("fr", "en"):
    rows = posts_for(lang)
    with (here / f"posts-{lang}.csv").open("w", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=list(rows[0]))
      writer.writeheader()
      writer.writerows(rows)
    print(lang, len(rows))


if __name__ == "__main__":
  main()
