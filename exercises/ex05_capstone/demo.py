"""Block 5 — the supervised team against the real model server.

    uv run python -m exercises.ex05_capstone.demo

Streams the graph so you can watch each decision as it is made.
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import build_graph

QUESTIONS = [
    "What does the Machine Learning course cover?",
    "What is the scope of the M.Tech Data Science programme?",
    "What is the fee for the hostel?",  # not in the corpus — watch it give up
]


def main() -> None:
    model = chat_model()
    graph = build_graph(model)

    for question in QUESTIONS:
        print(f"\n{'=' * 70}\nQ: {question}\n{'=' * 70}\n")

        draft, steps, rounds = "", 0, 0

        # stream() reports each node's update as it happens, so the run is
        # narrated live rather than appearing all at once at the end.
        for event in graph.stream(
            {"question": question, "notes": [], "draft": "", "steps": 0, "next": ""}
        ):
            for node, update in event.items():
                if node == "supervisor":
                    steps = update["steps"]
                    print(f"  supervisor (step {steps}): {update['next']}")
                elif node == "research":
                    rounds += 1
                    note = " ".join(update["notes"][0].split())
                    print(f"  researcher: {note[:160]}...")
                elif node == "write":
                    draft = update["draft"]
                    print("  writer: drafted an answer")

        if draft:
            print(f"\nA: {draft}")
        else:
            # Reaching the budget without ever writing is a real outcome, not a
            # crash, and printing an empty answer would hide it.
            print(
                "\nA: (nothing was written — the supervisor spent the whole "
                "budget on research)"
            )
        print(f"   ({steps} supervisor decisions, {rounds} research rounds)")

    print(f"\n\n{'=' * 70}\nWhat to look at\n{'=' * 70}")
    print(
        "\nThe questions took different routes through the same graph. Nobody "
        "\nwrote an if-statement for that: the supervisor decided each time."
        "\n"
        "\nNow look at the step counts, because they are not all the same, and "
        "\nthe untidy one is the most useful thing in this demo."
        "\n"
        "\nA clean run is three decisions: RESEARCH, WRITE, DONE. But you will "
        "\nusually see at least one question where the supervisor keeps saying "
        "\nWRITE, re-writing an answer it already has, until it hits the step "
        "\nbudget at 8. The final answer is fine. Six model calls were wasted "
        "\ngetting there."
        "\n"
        "\nThat is not a bug in the code, and it is not something a better "
        "\nprompt reliably fixes — this prompt has already been through several "
        "\nrounds of exactly that. It is what supervising with a language model "
        "\nis actually like. The model is agreeable; asked whether the answer "
        "\ncould be improved, 'yes' is always defensible."
        "\n"
        "\nSo the budget is not a safety net you hope never to need. It is load "
        "\nbearing, it fires on ordinary questions, and it is the only reason "
        "\nthat run terminated at all. Set MAX_STEPS to 2 and re-run to see the "
        "\nother side of the trade: it stops sooner and answers worse."
    )


if __name__ == "__main__":
    main()
