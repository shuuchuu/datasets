# French Press 1914, Questions and Answers

20 questions about `french-press-1914-passages`, for evaluating a question answering
(RAG) system: 18 whose answer is stated in one passage, and 2 the corpus can't answer,
which the system should decline.

## Files

- `questions.jsonl`: one question per line: `id`, `question`, `answer` (a reference
  answer, `null` for the 2 unanswerable questions), `passage_ids` (the passages of
  `french-press-1914-passages` that state the answer; empty when there is none).

Written by an LLM (Claude) from passages read in full, each answer checked against its
passage, for shuuchuu's text mining labs.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The passages themselves are
public domain.
