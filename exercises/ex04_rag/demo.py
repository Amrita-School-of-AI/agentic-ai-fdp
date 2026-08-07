"""Block 4 — retrieval against the real corpus, model and embedding server.

    uv run python -m exercises.ex04_rag.demo

Indexing roughly 350 KB of curriculum takes a few seconds the first time.
"""

from __future__ import annotations

import time

from agentic_fdp import chat_model, embeddings

from .agent import answer, build_index, load_corpus, split

QUESTIONS = [
    "How many credits does the M.Tech in Data Science require in total?",
    "Which semester has the project work, and what is it worth?",
    "What mathematics courses are in the first semester?",
    "What is the attendance requirement for the hostel mess?",  # not in the corpus
]


def main() -> None:
    print("loading corpus...")
    docs = load_corpus()
    for d in docs:
        print(f"  {d.metadata['source']:<45} {len(d.page_content):>7,} characters")

    chunks = split(docs)
    print(f"\nsplit into {len(chunks)} chunks")

    print("embedding and indexing (this is the slow step)...")
    t = time.time()
    index = build_index(chunks, embeddings())
    print(f"indexed in {time.time() - t:.1f}s")

    model = chat_model()

    for q in QUESTIONS:
        print(f"\n{'=' * 70}\nQ: {q}\n{'=' * 70}")

        text, used = answer(model, index, q, k=4)

        print("\nretrieved:")
        for c in used:
            preview = " ".join(c.page_content.split())[:100]
            print(f"  [{c.metadata['source']}] {preview}...")

        print(f"\nA: {text}")

    print(
        "\n\nThe last question is not answerable from these documents. A "
        "\ngrounded agent says so. An ungrounded one invents a plausible "
        "\nattendance percentage, and you would have no way to tell."
    )


if __name__ == "__main__":
    main()
