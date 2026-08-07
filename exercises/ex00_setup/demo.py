"""Block 0 — the same code, against the real model server.

    uv run python exercises/ex00_setup/demo.py
"""

from __future__ import annotations

from agentic_fdp import chat_model

from .agent import ask, ask_as

QUESTION = "In two sentences, what is an AI agent?"

ROLES = [
    "You are a strict examiner. Answer in one line, no examples.",
    "You are an encouraging tutor speaking to a first-year student. Use one everyday example.",
]


def main() -> None:
    model = chat_model()

    print(f"Q: {QUESTION}\n")
    print("--- no system message ---")
    print(ask(model, QUESTION))

    for role in ROLES:
        print(f"\n--- {role} ---")
        print(ask_as(model, role, QUESTION))

    print(
        "\nSame model, same question, three different answers. The system "
        "message is doing all of that work."
    )


if __name__ == "__main__":
    main()
