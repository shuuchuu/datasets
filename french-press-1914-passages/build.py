"""Build passages.parquet from ../french-press-1914 (run from this directory).

    uv run --no-project --with pandas --with pyarrow --with wordfreq python build.py

For each issue: join its pages, rejoin the words the OCR split at a line end
("con- tinuer", "con-\ntinuer") when the joined word is French (wordfreq), then
pack the lines (a line over 250 words cut into its sentences) into passages
of 100 to 250 words, ending at a sentence end when possible (a sentence over
250 words stays whole). A
passage's `noise` is the share of its words wordfreq doesn't know; passages
above 0.15 are dropped, and exact duplicates (case and spaces aside) too.
"""

import hashlib
import json
import re
from pathlib import Path

import pandas as pd
from wordfreq import zipf_frequency

MIN_WORDS, MAX_WORDS, MAX_NOISE = 100, 250, 0.15
WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")
SPLIT = re.compile(r"([^\W\d_]+)-\s+([^\W\d_]+)")
END = re.compile(r"[.!?»]\s*$")
SENTENCE = re.compile(r"(?<=[.!?»])\s+(?=[«—A-ZÀ-Ý])")
_known: dict[str, bool] = {}


def known(word: str) -> bool:
    word = word.lower()
    if word not in _known:
        _known[word] = zipf_frequency(word, "fr") > 0
    return _known[word]


def rejoin(text: str) -> str:
    def fix(match: re.Match[str]) -> str:
        joined = match[1] + match[2]
        return joined if known(joined) else match[0]

    return SPLIT.sub(fix, text)


def noise(text: str) -> float:
    words = [w for w in WORD.findall(text) if len(w) > 1]
    return sum(not known(w.split("'")[-1].split("’")[-1]) for w in words) / max(len(words), 1)


def segments(text: str) -> list[str]:
    """The issue's lines, a line longer than MAX_WORDS cut into its sentences."""
    out = []
    for line in text.split("\n"):
        line = " ".join(line.split())
        if not line:
            continue
        out.extend(SENTENCE.split(line) if len(line.split()) > MAX_WORDS else [line])
    return out


def passages(text: str) -> list[str]:
    out, current, n = [], [], 0
    for segment in segments(text):
        size = len(segment.split())
        if current and n + size > MAX_WORDS:
            if n >= MIN_WORDS:
                out.append(" ".join(current))
            current, n = [], 0
        current.append(segment)
        n += size
        if n >= MIN_WORDS and END.search(segment):
            out.append(" ".join(current))
            current, n = [], 0
    if n >= MIN_WORDS:
        out.append(" ".join(current))
    return out


rows, seen = [], set()
for path in sorted(Path("../french-press-1914").rglob("*.json")):
    issue = json.loads(path.read_text(encoding="utf8"))
    newspaper, date = issue["title"][0], issue["date"][0]
    text = rejoin("\n".join(issue["contentAsText"]))
    for i, passage in enumerate(passages(text)):
        key = hashlib.sha1(" ".join(passage.lower().split()).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        score = noise(passage)
        if score <= MAX_NOISE:
            rows.append((f"{path.parent.parent.parent.name}-{date}-{i:03d}", newspaper, date, passage, len(passage.split()), round(score, 3)))

df = pd.DataFrame(rows, columns=["id", "newspaper", "date", "text", "n_words", "noise"])
df["date"] = pd.to_datetime(df["date"])
df.to_parquet("passages.parquet", index=False)
print(df.groupby("newspaper").size(), len(df), df.n_words.describe(), sep="\n")
