"""Block 2 — chaining and routing against the real model server.

    uv run python -m exercises.ex02_chaining_routing.demo
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import chain, route_and_answer

ARTICLE = """
The Amrita School of AI runs a SLURM cluster called asaicompute for teaching and
research. It has three nodes with six GPUs between them: two RTX 6000 Ada cards
on the head node and four A100 80GB cards across the two compute nodes. Home
directories are shared over GlusterFS, so a user sees the same files on every
node. Jobs are submitted through a single partition and scheduled by fairshare,
and most interactive work arrives through an Open OnDemand web portal rather
than over SSH.
"""

QUESTIONS = [
    "If a job needs 4 GPUs and each node has 2, how many nodes must I request?",
    "How many credits does 23AID304 carry?",
    "What should I read to learn about SLURM?",
]


def main() -> None:
    model = chat_model()

    print("=" * 70)
    print("PART A — chaining")
    print("=" * 70)

    facts, headline = chain(model, ARTICLE)
    print("\nstage 1 output (the facts):\n")
    print(facts)
    print("\nstage 2 output (headline, written from the facts above):\n")
    print(f"  {headline}")
    print(
        "\nThe middle value is the point. When the headline is wrong you can "
        "\nsee whether the extraction or the compression failed."
    )

    print("\n\n" + "=" * 70)
    print("PART B — routing")
    print("=" * 70)

    for q in QUESTIONS:
        route, answer = route_and_answer(model, q)
        print(f"\nQ: {q}")
        print(f"   routed to: {route}")
        print(f"   {answer}")

    print(
        "\n\nThree different personalities, one model. The only thing that "
        "\nchanged between them was the system message."
    )


if __name__ == "__main__":
    main()
