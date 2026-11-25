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

The course's agent chapters use `agent/` instead (below): the shop's customer-support
agent, which reads a customer's message, calls the shop's tools (an order's record, the
stock, the policies, a ticket, a hand-over to a person), then replies as the charter
says. Its labs build a tool-calling training set from it, fine-tune a small model on it,
plug the model into the agent and compare it with the base model on a frozen
evaluation set.

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
- `lab-results/agent-sft-<train|validation>.jsonl`: the agent's tool-calling training
  set, which the lab `genai/fine-tuning/tool-calling/support-tool-calls-datasets` of
  shuuchuu's labs builds from `agent/` (below), its solutions run as they stand: 599 / 63
  examples in TRL's conversational format with tools. `messages`: the agent's system
  prompt (the one the agent chapters give it), the customer's message, each call in an
  `assistant` message's `tool_calls` with its arguments as a JSON string, its result in
  a `tool` message, then the reply; `tools`: the five schemas of `agent/outils.json`, as
  a JSON string (TRL's `SFTTrainer` reads it); `id`, `source` (`erreur` and `voisin`:
  the requests the reference agent got wrong on a sample of the pool, and others of
  their scenarios; `historique`: the rest of the pool; `synthetique`) and `classe` (the
  expected calls). Up to 80 examples per class, split by phrasing (`gabarit`), none near
  `agent/eval.jsonl`. This version comes from a run without a GPU: Qwen3-0.6B as the
  reference agent on 12 requests, Qwen3-1.7B writing 4 synthetic messages, of which
  none passed the filters and the charter, so the rare classes keep their pool counts
  (`hors_sujet` 8, `refus` 13, `remerciement` 35). A run on a GPU (Qwen3-1.7B on 224
  requests, Qwen3-4B-Instruct-2507 for about 300 synthetic messages) is to replace it.
  The fine-tuning lab of the agent loads it, so it doesn't depend on each trainee's run.
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

## The agent's data (`agent/`)

The data of the customer-support agent of Biclou & Cie, which the course's agent
chapters build, fine-tune and evaluate: its tools, what they read, and requests
annotated with what the agent must do. Same scenarios as the tickets, plus three groups
the agent answers without a tool.

### Files

- `outils.json`: the five tools' JSON schemas, as `transformers.utils.get_json_schema`
  writes them from the labs' Python functions (French names and descriptions). Their
  `return` key describes the result for the reader: the labs remove it before showing the
  schemas to a model (an MCP server doesn't declare it, and the serving engines don't
  write it in the prompt), which reads 135 fewer tokens.
- `commandes.csv`: what `chercher_commande` reads, 603 orders: every order number a
  request names (303), and 300 that none does, of every status, for the labs' synthetic
  examples. Columns: `numero` (`CMD-` and 6 digits), `date_commande`, `canal`
  (`en_ligne`, `magasin`), `magasin` (a store purchase's city), `articles`, `montant`
  (euros), `paiements` (2 for a double charge), `statut` (`en_preparation`, `expediee`,
  `livree`, `retour_en_controle`, `remboursee`, `retiree_en_magasin`), `transporteur`
  (three made-up carriers), `numero_suivi`, `date_expedition`, `dernier_suivi` (the last
  tracking event of a parcel still on its way), `date_livraison`, `date_retour_recu`.
  Dates are `YYYY-MM-DD`, consistent with what the request says (a parcel late by 8 to
  12 days, lost for more than 10 working days, a return received and being checked...).
- `stock.csv`: what `verifier_stock` reads, the stock of 2026-11-16: `modele` (the 11
  bikes), `taille` (`S` to `XL`), `magasin` (the six stores), `quantite` (0 for 78 of the
  264 rows), `reassort` (the next delivery, for the rows at 0).
- `demandes.jsonl`: the pool, 1,300 requests of 2026-10-01 to 2026-11-15, the
  annotated history the labs draw their training data from. One JSON object per line:
  - `id` (`D-0001`, in date order), `date`, `canal`, `langue` (`fr`, or `en` for 32);
  - `scenario` (the tickets' 32, plus `remerciement`, `hors_sujet`, `refus`), `gabarit`
    (the phrasing: `<scenario>/<langue>/<index>`), `cas` (`nominal`; `sans_numero`, an
    order follow-up without its number; `commande_introuvable`, a number the system
    doesn't know), `categorie` and `priorite` (the scenario's, empty for the three new
    groups), `bruit` (the message's noise: `fautes`, `sans accents`, `capitales`);
  - `message`: the customer's message, signed or not, with the noise of the tickets
    (typos, no accents, `Bjr`), no personal data but a name;
  - `appels_attendus`: the calls the agent must make, in order, each
    `{"name": ..., "arguments": {...}}`, empty for no tool;
  - `resultats_outils`: what each call returns, from the files above;
  - `reponse`: the reply that follows, as the charter says and consistent with the
    results (the parent's replies, plus the facts of the order's record, the stock, the
    ticket's or the hand-over's number).
- `eval.jsonl`: the frozen evaluation set, 139 requests of 2026-11-16 to 2026-11-19
  (`E-001`...), in the same format. The models the agent chapters compare are measured
  on it, and nothing is trained on it: its messages come from phrasings the pool never
  uses (one or two per scenario, held out), none of its order numbers is in the pool, and
  no message is near a pool one (the highest word-trigram Jaccard is 0.15). Only the
  messages are held out: the reference replies come from the same templates as the
  pool's (130 of the 139 are at 0.6 or more from a pool reply, 15 are identical), so
  a score against their text favors a model trained on the pool. Compare models on
  their calls, or on the facts of their replies.
- `generate.py`: writes them (`python agent/generate.py`, standard library only, seeded:
  the same bytes each run) and prints the counts below. It imports `../generate.py`'s
  scenarios and slots, and doesn't change `tickets.csv` nor `test.jsonl`.

### The tools

| Tool | Arguments | Returns |
| --- | --- | --- |
| `chercher_commande(numero)` | `numero`: `CMD-` and 6 digits | the order's row without its empty fields; `{"erreur": ...}` for a number not in the file or not in this format |
| `verifier_stock(modele, taille, magasin)` | `modele`: one of the 11 bikes; `taille`: `S`, `M`, `L`, `XL`; `magasin`: one of the six cities | `modele`, `taille`, `magasin`, `quantite`, and `reassort` when it is 0; `{"erreur": ...}` for a value not in the file |
| `chercher_politique(theme, question)` | `theme`: `retours`, `livraison`, `garantie`, `atelier`, `location`, `facturation`, `compte`, `magasins`, `tailles` (the sections of `charte.md`'s policy); `question`: free text | `theme` and `passages`: up to 3 sentences of the section, those sharing the most words with the question (words of 4 letters or more, compared by their first 5 letters, accents and case aside; document order between ties) |
| `creer_ticket(categorie, priorite, resume)` | `categorie`: the 7 categories; `priorite`: `basse`, `normale`, `haute`; `resume`: free text | `ticket` (`T-2xxxx`), `statut` |
| `escalader(raison, resume)` | `raison`: `securite`, `colis_perdu`, `paiement`, `accident_location`, `vol_location`; `resume`: free text | `dossier` (`ESC-xxxx`), `equipe`, `recontact` |

Every argument but `question` and `resume` is compared exactly when the labs score a
call; those two are free text.

### The behavior

One correct behavior per message, from its scenario:

1. A message that gives an order number (`CMD-` and 6 digits): `chercher_commande`
   first, whatever the scenario.
2. Then the scenario's action:

| Action | Scenarios |
| --- | --- |
| `chercher_politique`, `theme` | `horaires` (`magasins`); `taille` (`tailles`); `choix_vae`, `garantie_info` (`garantie`); `delai_info` (`livraison`); `revision` (`atelier`); `mauvaise_taille`, `retour_utilise`, `retour_hors_delai` (`retours`); `location_modif`, `location_tarifs`, `location_annulation` (`location`); `facture` (`facturation`); `mot_de_passe`, `changer_email` (`compte`) |
| `verifier_stock`, the bike, the frame size and the city the message names | `stock` |
| `creer_ticket`, the scenario's `categorie`, `priorite` `normale` | `colis_abime`, `crevaison`, `freins_grincent`, `batterie_charge`, `derailleur`, `prix_promo`, `suppression_compte` |
| `escalader`, `raison` | `freins_defaillants`, `batterie_surchauffe` (`securite`); `colis_perdu`; `double_debit` (`paiement`); `location_accident` (`accident_location`); `location_vol` (`vol_location`): the charter's `haute`, safety and money, always, number or not |
| Nothing more: the record answers | `colis_retard`, `changer_adresse`, `remboursement_attente`; without a number, no tool, and the reply asks for it (`cas` `sans_numero`); with a number the system doesn't know, the reply asks to check it (`commande_introuvable`, 8 % of these) |
| No tool | `remerciement` (thanks, an acknowledgement), `hors_sujet` (the weather, a cover letter, a restaurant...), `refus` (another customer's details, an inflated invoice, a discount under threat, unrestricting an e-bike, a prompt injection) |

So a request makes 0, 1 or 2 calls, each in its own assistant turn, in this order.

### Counts

| Expected calls | Pool | Share | Eval |
| --- | --- | --- | --- |
| `chercher_politique` | 556 | 42.8 % | 25 |
| `creer_ticket` | 191 | 14.7 % | 15 |
| `chercher_commande` | 108 | 8.3 % | 15 (3 numbers unknown) |
| `verifier_stock` | 97 | 7.5 % | 15 |
| `escalader` | 81 | 6.2 % | 15 |
| `chercher_commande`, `escalader` | 75 | 5.8 % | 8 |
| `chercher_commande`, `creer_ticket` | 49 | 3.8 % | 8 |
| `chercher_commande`, `chercher_politique` | 42 | 3.2 % | 8 |
| None: order number missing | 40 | 3.1 % | 10 |
| None: thanks | 37 | 2.8 % | 6 |
| None: a request to refuse | 16 | 1.2 % | 8 |
| None: off-topic | 8 | 0.6 % | 6 |

The pool follows the tickets' shares of the scenarios: what the agent's history holds,
with few negatives and few calls in a row, from 106 phrasings. The evaluation set is
balanced over the tools and the negatives, from 43 phrasings. The pool has 1,268
messages in French and 32 in English; the evaluation set, 134 and 5. Noise in the pool:
128 messages with typos, 85 without accents, 16 in capitals.

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
