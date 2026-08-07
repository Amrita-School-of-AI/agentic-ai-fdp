"""Block 5 — the supervised team against the real model server.

    uv run python -m exercises.ex05_capstone.demo

Streams the graph so you can watch each decision as it is made.
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import build_graph

QUESTIONS = [
    "How many credits does the M.Tech in Data Science require, and what is the project worth?",
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

        print(f"\nA: {draft}")
        print(f"   ({steps} supervisor decisions, {rounds} research rounds)")

    print(
        "\n\nThe two questions took different routes through the same graph. "
        "\nNobody wrote an if-statement for that; the supervisor decided each "
        "\ntime, and the step budget guaranteed both runs would end."
    )


if __name__ == "__main__":
    main()
