# Synthetic Bluesky posts about Ikea

416 French and 428 English **synthetic** posts that mention Ikea, shaped like the
results of Bluesky's search API: the fallback of the Bluesky text mining demo of
shuuchuu's labs (`mlops/data/processing/bluesky-text-mining`), for when Bluesky's API
doesn't answer, and the run whose outputs the demo stores. In class, the demo collects
real posts live.

## Why synthetic

Real posts aren't redistributed here: under Bluesky's Terms of Service (2025-08-14,
section 3), users keep the ownership of their posts and license them to Bluesky only,
and a post stays personal data under the GDPR even without its author (its text can be
searched). A dataset of Bluesky posts published on Hugging Face in 2024 was taken down
after a backlash over consent.

## Files

- `posts-fr.csv`, `posts-en.csv`: one post per row. Columns, those the demo keeps from
  a real post after anonymizing it: `post_id` (random, 16 hex digits), `created_at`
  (UTC, 2026-08-20 to 2026-10-17), `text`, `likes`, `reposts`, `replies`.
- `generate.py`: writes both files (`python generate.py`, standard library only,
  seeded).

Every text is written from `generate.py`'s templates, by Shuuchuu, no real post among
them. Its topics: furniture assembly, delivery, customer service, prices, the
restaurant, second hand and sustainability, products, the store, plus three peaks (the
autumn collection on 2026-09-10, a website outage on 2026-09-25, a sales weekend on
2026-10-03/04). Its noise, the one a real search returns and the demo cleans: links,
masked mentions (`@anonyme`, `@anonymous`), hashtags, emojis, `IKEA`/`Ikéa` spellings,
about 8 % of posts in the other language, posts with no words (a link and emojis), and
a deals bot posting the same text several times a day. The events are invented and
say nothing of the real company.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
