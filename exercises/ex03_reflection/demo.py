"""Block 3 — reflection against the real model server.

    uv run python -m exercises.ex03_reflection.demo

Runs two briefs on purpose. One the model tends to satisfy first time, one it
usually does not. The comparison is the point: reflection is not free, and
whether it earns its cost depends entirely on the task.
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import reflect

EASY = (
    "Write an explanation of what a SLURM job scheduler does, for a first-year "
    "engineering student who has never used a cluster.\n"
    "Constraints, all of which must be met:\n"
    "  1. Between 55 and 65 words.\n"
    "  2. Exactly one example, and it must contain at least two numbers.\n"
    "  3. It must explain why a job waits rather than running immediately.\n"
    "  4. Do not use any of these words: resource, orchestrate, allocate, "
    "manage, efficient, leverage.\n"
    "  5. End with a sentence, not a question."
)

# Harder, because the forbidden list removes almost every word the topic
# naturally reaches for, and an exact word count is something models are
# reliably poor at.
HARD = (
    "Explain gradient descent to someone who has never studied calculus.\n"
    "Constraints, all of which must be met:\n"
    "  1. Exactly 40 words. Not 39, not 41.\n"
    "  2. It must use the word 'hill'.\n"
    "  3. It must NOT use any of these words: learn, learning, model, data, "
    "train, training, loss, error, minimum, optimise, optimize, function, "
    "algorithm, parameter, weight.\n"
    "  4. No numbers anywhere.\n"
    "  5. It must say what happens when the slope becomes flat."
)


def show(model, label: str, brief: str) -> None:
    print(f"\n\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(brief)

    result = reflect(model, brief, max_rounds=3)

    for i, draft in enumerate(result.drafts):
        print(f"\n{'-' * 70}\ndraft {i + 1}\n{'-' * 70}\n{draft}")
        if i < len(result.critiques):
            print(f"\ncritique of draft {i + 1}:\n{result.critiques[i]}")

    calls = 1 + result.rounds + (len(result.drafts) - 1)
    print(f"\n  rounds     : {result.rounds}")
    print(f"  approved   : {result.approved}")
    print(f"  model calls: {calls}  (one call would have produced draft 1 alone)")


def main() -> None:
    model = chat_model()

    show(model, "BRIEF A — the model usually gets this right first time", EASY)
    show(model, "BRIEF B — the model usually needs at least one revision", HARD)

    print(f"\n\n{'=' * 70}\nThe point of running both\n{'=' * 70}")
    print(
        "\nCompare draft 1 with the final draft in each case."
        "\n"
        "\nIn brief A the first draft was very likely already correct, so the "
        "\ncritique and any revision cost you two or more extra calls and bought "
        "\nnothing. In brief B the first draft almost certainly broke a "
        "\nconstraint, the critic caught it by name, and the revision fixed it. "
        "\nSame pattern, same code, opposite verdict on whether it was worth it."
        "\n"
        "\nThat is the whole engineering judgement in this block. Reflection is "
        "\nten lines. Knowing which of these two situations you are in is the "
        "\npart that takes measurement, which is why reflect() keeps every draft "
        "\nand every critique instead of returning only the final text."
    )


if __name__ == "__main__":
    main()
