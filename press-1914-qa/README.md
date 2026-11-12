# French Press 1914, Questions and Answers

20 questions about `french-press-1914-passages`, for evaluating a question answering
(RAG) system: 18 whose answer the corpus states, each with the passages found to
state it (one for 16 of them, 2 and 6 for questions 3 and 8), and 2 the corpus can't
answer, which the system should decline.

## Files

- `questions.jsonl`: one question per line: `id`, `question`, `answer` (a reference
  answer, `null` for the 2 unanswerable questions), `passage_ids` (every passage of
  `french-press-1914-passages` found to state the answer; empty when there is none).

Written by an LLM (Claude) from passages read in full, each answer checked against its
passage, for shuuchuu's text mining labs. The other passages that state the answers
of questions 3 and 8, found by reviewing the retrieval failures, were added since.

## License

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). The passages themselves are
public domain.
