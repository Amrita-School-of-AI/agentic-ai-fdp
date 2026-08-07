"""Block 3 — reflection against the real model server.

    uv run python -m exercises.ex03_reflection.demo
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import reflect

BRIEF = (
    "Write a 60-word explanation of what a SLURM job scheduler does, for a "
    "first-year engineering student who has never used a cluster. Include one "
    "concrete example with numbers. Do not use the words 'resource' or "
    "'orchestrate'."
)


def main() -> None:
    model = chat_model()

    print(f"BRIEF\n{'-' * 70}\n{BRIEF}\n")

    result = reflect(model, BRIEF, max_rounds=3)

    for i, draft in enumerate(result.drafts):
        print(f"\n{'=' * 70}\nDRAFT {i + 1}\n{'=' * 70}\n{draft}")
        if i < len(result.critiques):
            print(f"\n--- critique of draft {i + 1} ---\n{result.critiques[i]}")

    print(f"\n{'=' * 70}")
    print(f"rounds run : {result.rounds}")
    print(f"approved   : {result.approved}")
    print(f"model calls: 1 draft + {result.rounds} critiques + "
          f"{len(result.drafts) - 1} revisions")
    print(
        "\nCompare draft 1 with the final one. If the difference is small, "
        "\nreflection was not worth three times the cost for this brief. That "
        "\njudgement is the real skill; the pattern itself is ten lines."
    )


if __name__ == "__main__":
    main()
