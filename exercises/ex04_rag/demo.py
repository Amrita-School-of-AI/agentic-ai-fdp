"""Block 4 — retrieval against the real corpus, model and embedding server.

    uv run python -m exercises.ex04_rag.demo

Indexing roughly 350 KB of curriculum takes a few seconds the first time.
"""

from __future__ import annotations

import time

from agentic_fdp import chat_model, embeddings

from .agent import answer, build_index, load_corpus, split

QUESTIONS = [
    # Answerable, and from one document only — watch the citation.
    "What is the scope of the M.Tech Data Science programme?",
    "Which courses are in Semester I of the M.Tech in Artificial Intelligence?",
    "What does the Foundations of Artificial Intelligence course cover?",
    # Answerable in principle, but the retriever struggles. See the closing note.
    "Which semester has the project work, and what is it worth?",
    # Genuinely not in the corpus. A grounded agent says so.
    "What is the attendance requirement for the hostel mess?",
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

    print(f"\n\n{'=' * 70}\nWhat just happened\n{'=' * 70}")
    print(
        "\n1. The first three worked, and cited the right document. Note that "
        "\n   the Semester I question pulled only from the AI curriculum, not "
        "\n   the Data Science one. That is retrieval discriminating between two "
        "\n   documents that share most of their vocabulary."
        "\n"
        "\n2. The project question probably failed, and the reason is worth more "
        "\n   than the successes. Look at what came back: the same 'Evaluation "
        "\n   Pattern' boilerplate, several times over. A curriculum document "
        "\n   repeats that block under every single course, so those chunks are "
        "\n   near-identical and they crowd out the one passage that actually "
        "\n   answers the question."
        "\n"
        "\n   Real corpora are full of this. Boilerplate, headers, footers and "
        "\n   repeated tables dominate a retriever that treats every chunk as "
        "\n   equally worth returning. Deduplicating near-identical chunks "
        "\n   before indexing is usually the first thing worth doing to a RAG "
        "\n   system that underperforms, and it is not a model problem at all."
        "\n"
        "\n3. The last question is not answerable from these documents, and the "
        "\n   agent said so rather than inventing a percentage. That refusal is "
        "\n   the grounding prompt doing its job."
    )


if __name__ == "__main__":
    main()
