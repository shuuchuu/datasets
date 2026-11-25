# French Press 1914, Questions and Answers

Questions about `french-press-1914-passages` for evaluating a question answering
(RAG) system, real answers of such a system with annotations, for checking an LLM
judge against them, and generated questions for training one (RAFT, a fine-tuned
encoder), drawn away from the test passages.

## Files

- `questions.jsonl`: 20 questions written one by one from passages read in full, one per
  line: `id`, `question`, `answer` (a reference answer, `null` for the 2 unanswerable
  questions), `passage_ids` (every passage of `french-press-1914-passages` found to
  state the answer; empty when there is none). 18 have an answer the corpus states, each
  with the passages found to state it (one for 15 of them, 4, 2 and 6 for questions 2, 3
  and 8), and 2 the corpus can't answer, which the system should decline (questions 19
  and 20).
- `synthetic-questions.jsonl`: 60 questions generated from the corpus, one per line,
  each with an expert's verdict (43 valid): `id` (101 to 160, apart from the 20 above),
  `question`, `answer` (the reference answer: the generated one, or the expert's
  rewording when it was right but badly put), `generated_answer` (the generator's own),
  `source_passage_id` (the passage the question was generated from), `passage_ids`
  (the passages that state the answer, the source first; the source alone for a
  rejected question), `usable` (the generator's own `exploitable` flag), `valid` (the
  expert's verdict), `reason` (why it was rejected, `null` when valid), `note` (the
  expert's remark, `null` when there is none). The reasons:
  - `not-standalone` (5): the question can't be understood without its passage: it
    points to the article, or names nothing (person, place, event) that identifies
    what it asks about;
  - `opinion` (4): it asks what a writer thinks, not a fact;
  - `fiction` (2): a serial novel or a literary text;
  - `not-usable` (2): the passage holds no fact to ask about (stock quotations, an
    advertisement);
  - `vague` (1): several answers would be right, other articles answer otherwise;
  - `ocr-noise` (1): the question rests on a word the OCR misread;
  - `false-premise` (1): the question states something the corpus contradicts;
  - `wrong-answer` (1): the generated answer is wrong.

  No question confused the issue's date with the event's: each date was checked
  against the passage's "hier" or "aujourd'hui". 41 questions name the newspaper (they
  match `Humanité|Figaro`) and a date ("d'après L'Humanité du 5 janvier 1914"), a
  phrasing readers seldom use and that the passages' text doesn't contain; they were
  kept when otherwise valid (25).
- `annotated-answers.jsonl`: 57 real answers of the RAG that the lab
  `genai/rag/evaluation/press-rag-evaluation-ragas` of shuuchuu/slides evaluates (not of
  the models that `genai/fine-tuning/rag/press-rag-raft-trl` compares), one per line,
  annotated (by an LLM standing in for the annotator, not by Ragas, see below): `id`,
  `question_id` (an `id` of the two files above), `question`, `reference_answer` (`null`
  when the question has none), `configuration` (the lab's name of the retrieval that
  served the passages, one of two: `dense`, the dense retrieval alone, or
  `hybride+reclassement`, BM25 and dense fused by RRF, then the first 30 reranked by a
  cross-encoder), `served_passage_ids` (the 5 passages of the prompt, in order), `found`
  (`false` when the system declined, by its own flag), `response` (its answer as it
  wrote it, even when it declined), `cited_passage_ids` (the served passages it cites),
  `faithful` (it states nothing the served passages don't; a refusal is faithful),
  `correct` (it says what the reference answer says; a refusal is correct when the
  question has no answer), `note`. By the `found` flag, among them: 29 faithful and
  correct answers, 9 unfaithful and wrong, 2 unfaithful but correct, 1 faithful but
  wrong, 13 wrong refusals (12 of them justified by passages that lack the answer:
  retrieval failures) and 3 right ones. One of the 29, answer 24, is a refusal in its
  text only (question 20, which has no answer): it says that the number isn't stated,
  but its flag is true, so a script that reads the flag alone counts an answer where the
  system should have declined.
- `training-questions.jsonl`: 619 generated questions for training, not reviewed, one
  per line: `id` (1001 to 1619), `question`, `answer` (the generated short answer),
  `quote` (the excerpt of the passage, copied verbatim with its OCR errors, that bears
  the answer, up to the spelling of a number and the date of an event, which may come
  from the issue's date, as the prompt asks: the citation of a RAFT target answer),
  `passage_id` (the passage the question was generated from, the one known to state the
  answer), `split` (`train`, 557, or `validation`, 62). None comes from a passage of the
  test questions above.

## How they were made

`questions.jsonl` was written by an LLM (Claude) from passages read in full, each
answer checked against its passage, for shuuchuu's text mining labs. The other passages
that state the answers of questions 2, 3 and 8, found by reviewing the retrieval failures,
were added since. Question 20 was replaced: its first version, "Qui a remporté le
championnat de France de football en 1914 ?", passed for unanswerable, but the corpus
answers it twice, Lille in association football (`l_humanite-1914-04-06-195`) and
Perpignan in rugby (`l_humanite-1914-05-04-161`). An unanswerable question is checked by
searching the corpus for its answer: the new one asks for the attendance of the
association final, which the corpus reports without it (the passages on the final, its
two teams and the spectators of the matches of those days were read).

`synthetic-questions.jsonl`: generated by Claude (Sonnet, Anthropic) with the prompt of
the RAG evaluation lab (`genai/rag/evaluation/press-rag-evaluation-ragas` in
shuuchuu/slides, exercise 1, whose prompt then called the passage an "extrait"), one
call per passage, on the lab's sample of 60 passages (noise at most 0.05, 40 from
*L'Humanité* and 20 from *Le Figaro*, `random_state` 1914). The validation, the
rewordings and the search for the other passages that state each answer (BM25 and dense
retrieval with the question, the answer and its key terms, then reading) were done by an
LLM, Claude, standing in for the domain expert, in a context separate from the
generation, from each source passage read in full.

`annotated-answers.jsonl`: the answers were generated by Qwen3-1.7B (no thinking,
greedy decoding) with the lab's answer prompt, on 29 questions of the two files above,
each retrieved both ways (`dense`, then `hybride+reclassement`); one answer whose JSON
didn't parse was left out. The two answers to question 20 were generated again, in the
same way, when the question was replaced. The annotations were made by an LLM, Claude,
standing in for the human annotator, from the question, the reference answer and the
served passages read in full.

`training-questions.jsonl`: generated by Claude (Sonnet, Anthropic) with the prompt of
`synthetic-questions.jsonl`, plus two instructions (copy a verbatim quote of one to
three sentences, at most 40 words, that bears the answer; refer "hier" and the like to
the issue's date, and decline serial novels, literary texts and opinions), each
passage taken on its own, in batches of 60 to 85 passages per session. The 1,080
passages: noise at most 0.05, two thirds from *L'Humanité*, one third from *Le Figaro*
(`random_state` 2014 for the first 600, 2015 for 480 more), none among the 97 passages
the test questions named then (`passage_ids`, `source_passage_id`, rejected questions
included) nor with a cosine similarity above 0.75 to one of them
(`embeddings-512.npy`); both still hold for the 100 passages they name since question 2
got three more references (at most 0.63 for these three). The generator found 660
usable; the automatic filter of the RAG evaluation lab (exercise 2) then dropped 4 that
point to the text and 36 whose answer shares fewer than half its words of four letters
or more with the passage (mostly right answers that OCR noise or a number in figures
hides from the check), and every quote was checked to be in its passage. Since then, 23
questions whose answer said more than its quote were corrected: 19 answers cut down to
the quote, 5 quotes moved or extended (one question had both), still verbatim. Of the 25
questions closest to a test question (shared words), one, on the same event and with the
same answer as question 125, was dropped. The validation split is a random tenth
(`numpy` `default_rng(1914)`). No expert read them: some answers are wrong, as with any
generated set.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The passages themselves are
public domain.
