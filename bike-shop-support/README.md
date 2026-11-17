# Bike shop customer support tickets

Made-up export of the customer-support tool of Biclou & Cie, the fictional bike shop of
`bike-shop` (six stores: Lille, Amiens, Nice, Marseille, Nantes and Rennes), written for
shuuchuu's fine-tuning labs. No real customer, agent or company is in it.

The labs' task: from a customer's message, write the JSON object
`{"categorie": ..., "priorite": ..., "reponse": ...}`, the triage and the reply the
support desk's charter asks for. They measure a base model zero-shot and few-shot, clean
the raw export into a training set, fine-tune a small model with QLoRA, evaluate it
(exact match on `categorie` and `priorite`, ROUGE and an LLM judge on `reponse`), then
align its tone with DPO.

## Files

- `charte.md`: the support desk's reply guide, in French, about one page: the two labels,
  the writing rules (vouvoiement, greeting, 40 to 120 words, order number restated, one
  next step, no refund promised before a check, no bank details asked, sign-off, English
  for an English message) and the shop's policies. The prompt of the "prompt only"
  baseline.
- `tickets.csv`: the raw export, 2,408 rows (2,307 distinct tickets), 2024-09-01 to
  2026-08-31, UTF-8, `,` between fields, fields quoted when they hold a comma, a quote or
  a newline. Columns:
  - `ticket_id`: `T-` and 5 digits, in date order; unique except the rows exported twice;
  - `date`: `YYYY-MM-DDTHH:MM`;
  - `canal`: `email` (1,282 rows), `formulaire` (716), `chat` (410, only Tuesday to
    Saturday, 10:00 to 19:00);
  - `client`: the customer's name in the tool;
  - `objet`: the mail's subject, the form's drop-down choice, or `Conversation chat`;
  - `message`, `reponse`: the customer's message and the agent's reply;
  - `agent`: one of eight first names, empty for some open tickets;
  - `statut`: `resolu`, `ouvert` or `fusionne`;
  - `satisfaction`: the customer's rating, 1 to 5, empty for 750 rows (31 %), always for
    the tickets not resolved;
  - `categorie`, `priorite`: as the agent tagged them, noisy (below).
- `test.jsonl`: 150 examples the support team validated, one JSON object per line:
  `ticket_id`, `message`, `categorie`, `priorite`, `reponse` (below).
- `lab-results/support-sft-<train|validation|test>.jsonl`: the training set the data
  preparation lab of shuuchuu's labs (`genai/fine-tuning/data/support-training-data-datasets`)
  builds from `tickets.csv`, its solutions run as they stand: 1,190 / 133 / 150 examples
  in TRL's conversational prompt-completion format (`prompt`: the lab's system message
  and the cleaned customer message; `completion`: the assistant's JSON object with
  `categorie`, `priorite`, `reponse`), plus `categorie` as a class index, in the sorted
  order of the seven categories (`compte` 0 … `retour` 6). The training labs load it, so
  they don't depend on each trainee's cleaning.
- `generate.py`: writes `tickets.csv` and `test.jsonl` (`python generate.py`, standard
  library only, seeded: the same bytes each run) and prints the counts below.

## The tickets

Each ticket comes from one of 32 scenarios (a late parcel, a wrong size, a puncture after
a week, squeaking brakes against failing ones, a battery that won't charge or that
overheats, a rental booking moved, an accident or a theft with a rental bike, a double
charge, a missing invoice, a forgotten password, an account to delete, opening hours,
a model in stock in a store, the frame size for a height, ...), with three to six
phrasings of the message (polite, terse, angry, rambling, several questions) and two or
three replies following the charter, filled with slots: products with invented model
names (`Biclou Urbain E5`, `Biclou Rando 28`, accessories), store, order number
(`CMD-` and 6 digits), dates, amounts, heights. The reply greets the customer by the
name the message is signed with (`Bonjour Madame Martin,`), `Bonjour,` when it is
unsigned or signed with a first name only: the model sees the message, not the `client`
column. `generate.py` checks every reply meant to follow the charter (its greeting,
sign-off, 40 to 120 words, vouvoiement, the order number restated) and that a reply only
uses what its message says.

The true labels of the rows (from their scenario, before the agents' noise):

| `categorie` | Rows | Share |
| --- | --- | --- |
| `information` | 712 | 29.6 % |
| `livraison` | 493 | 20.5 % |
| `reparation` | 367 | 15.2 % |
| `retour` | 282 | 11.7 % |
| `location` | 235 | 9.8 % |
| `facturation` | 196 | 8.1 % |
| `compte` | 123 | 5.1 % |

`priorite`: `normale` 1,221 rows, `basse` 835 (general information), `haute` 352
(safety: brakes failing, an e-bike battery overheating, an accident or a theft during a
rental; money: a double charge, a parcel more than 10 working days late). Rentals peak
in summer, repairs in spring.

## The noise

What the labs' cleaning exercise finds, counted over the rows of the export (a row of a
day exported twice counts twice):

| Noise | Rows | Share |
| --- | --- | --- |
| Exact duplicates: every row of 31 days, exported twice | 101 | 4.2 % |
| Near duplicates: a customer re-sends a message, prefixed with `Relance :` or with a line added; half merged into the first ticket (`Ticket fusionné avec T-xxxxx`, `statut` `fusionne`), half answered again | 77 | 3.2 % |
| Unusable replies: empty (22), `voir mail` (24), `test` (25), `ok` (22), `cf. appel client` (23), `Ticket fusionné avec T-xxxxx` (16); `statut` `fusionne` for the merged ones, `ouvert` for half of the empty ones | 132 | 5.5 % |
| Open tickets with no reply, most of them from July and August 2026 | 63 | 2.6 % |
| Replies of Jordan, the agent who breaks the charter: tutoiement, a sentence or two, no greeting nor sign-off, sometimes an immediate refund promised (28 rows) | 162 | 6.7 % |
| Replies giving the 14-day return window (below) | 98 | 4.1 % |
| Messages with an e-mail address or a phone number | 233 | 9.7 % |
| Messages with a street address | 36 | 1.5 % |
| `formulaire` messages in HTML (`<p>`, `<br>`, `&nbsp;`, `&#39;`), about half of them | 372 | 15.4 % |
| `email` messages with a phone's signature (`Envoyé de mon iPhone`, ...) | 321 | 13.3 % |
| `email` messages quoting an earlier mail (`> ...`) | 78 | 3.2 % |
| Messages with typos | 215 | 8.9 % |
| Messages with no accents | 133 | 5.5 % |
| Messages in capitals | 26 | 1.1 % |
| Messages in English, answered in English as the charter says | 97 | 4.0 % |
| `categorie` or `priorite` empty (43 `categorie`, 39 `priorite`, 52 both) | 134 | 5.6 % |
| `categorie` or `priorite` spelled another way (`Livraison `, `REPARATION`, `réparation`, `info`, `normal`, `Haute`, ...) | 142 | 5.9 % |

Low ratings follow the bad replies: 99 of Jordan's 121 rated rows are rated 1 or 2,
against 161 of the other agents' 1,537 (angry customers, safety issues, unusable
replies). The messages themselves are sloppy on purpose (missing commas, `svp`, `Bjr`),
the replies are not.

## The return policy of 2025-06-01

The return window went from 14 to 30 days after delivery on 2025-06-01. Replies before
that date give 14 days, as was correct at the time (`dans les 14 jours suivant la
livraison`, `vous disposez de 14 jours après la livraison`), and contradict the current
charter, which the training set must follow. The refund delay, 14 days after the return
is received and checked, did not change: a `14 jours` in a reply is not always the
return window.

## The test set

`test.jsonl` holds 150 French examples drawn from the tickets of 2026-03-01 to
2026-08-31, stratified by category (`information` 40, `livraison` 28, `reparation` 22,
`retour` 18, `location` 16, `facturation` 14, `compte` 12), never a re-sent copy. Their
`message` is cleaned: no HTML, no phone signature, no quoted mail, and e-mail addresses,
phone numbers and street addresses replaced by `[EMAIL]`, `[TELEPHONE]` and `[ADRESSE]`
(typos and capitals stay, as a customer writes them). `categorie` and `priorite` are the
normalized labels, and `reponse` a reply written for the test, following the current
charter, whatever the original reply was.

The export holds the original row of each of these tickets (three of them twice), with
its original reply: 26 of them are empty, unusable or Jordan's. Training on the export
as it is leaks the test messages: the labs remove these `ticket_id` before training.

## Personal data

None real: the names are invented, the e-mail addresses use reserved or fictional
domains (`example.com`, `example.org`, `mail.test`, `exemple.fr`), the phone numbers the
ranges the French regulator ARCEP reserves for fiction (`01 99 00`, `02 61 91`,
`04 65 71`, `06 39 98`), the shop's own address is `support@biclou-et-cie.example`, and
the street addresses are generic names.

## Source

Written for shuuchuu's fine-tuning labs by Shuuchuu, from `generate.py`'s scenarios; the
tickets, customers and agents are invented.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
