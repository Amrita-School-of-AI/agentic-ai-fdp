"""A deliberately simple keyword search over the corpus. Provided for you.

Block 4 used embeddings. This uses word overlap, and it is here rather than the
vector index for one practical reason: the capstone is the last 75 minutes of
the day, and it should not be able to fail because a server is busy. This runs
entirely on your laptop.

It is also a fair reminder that retrieval does not have to mean embeddings.
Scoring by how many of the question's words appear in a passage is crude, works
surprisingly often, and costs nothing.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"

# Words too common to carry meaning. A real system would use a proper stop list;
# this is enough to stop "the" dominating every score.
STOP = {
    "the", "a", "an", "and", "or", "of", "in", "to", "for", "is", "are", "was",
    "were", "be", "on", "at", "by", "with", "as", "it", "this", "that", "what",
    "which", "how", "many", "does", "do", "i", "you", "from", "has", "have",
}


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]


@lru_cache(maxsize=1)
def _passages() -> tuple[tuple[str, str], ...]:
    """Every paragraph in the corpus, paired with its source file name."""
    out = []
    for path in sorted(CORPUS_DIR.glob("*.txt")):
        for para in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            cleaned = " ".join(para.split())
            if len(cleaned) > 120:
                out.append((path.name, cleaned))
    return tuple(out)


def search_corpus(query: str, k: int = 3) -> list[tuple[str, str]]:
    """Return the k passages sharing the most words with `query`.

    Each result is (source_file, passage).
    """
    terms = set(_words(query))
    if not terms:
        return []

    scored = []
    for source, passage in _passages():
        overlap = len(terms & set(_words(passage)))
        if overlap:
            scored.append((overlap, source, passage))

    scored.sort(key=lambda t: -t[0])
    return [(source, passage) for _, source, passage in scored[:k]]
