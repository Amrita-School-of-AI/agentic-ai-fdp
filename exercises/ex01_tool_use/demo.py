"""Block 1 — the tool-use loop against the real model server.

    uv run python -m exercises.ex01_tool_use.demo

Prints every step, so you can watch the model decide to call a tool, read the
result, and decide what to do next. Nobody scripted that sequence.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agentic_fdp import chat_model

from .agent import SYSTEM
from .tools import ALL_TOOLS

QUESTIONS = [
    "How many credits do 23AID304 and 24AIM332 come to together?",
    "Is 23AID311 worth more credits than 23MAT216?",
    "What is the capital of France?",  # needs no tools — watch it not call any
]


def verbose_trace(model, question: str) -> None:
    """The same loop as agent.py, printing each tool call as it happens.

    Spelled out here rather than calling run_agent, so that the printing does
    not clutter the loop you just wrote.
    """
    by_name = {t.name: t for t in ALL_TOOLS}
    bound = model.bind_tools(ALL_TOOLS)
    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=question)]

    print(f"\n{'=' * 70}\nQ: {question}\n{'=' * 70}")

    for step in range(1, 7):
        reply: AIMessage = bound.invoke(messages)
        messages.append(reply)

        if not reply.tool_calls:
            print(f"\nstep {step}: no tools wanted — this is the answer")
            print(f"\nA: {reply.content}")
            return

        for call in reply.tool_calls:
            result = by_name[call["name"]].invoke(call["args"])
            print(f"step {step}: {call['name']}({call['args']})")
            print(f"          -> {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    print("gave up after 6 steps")


def main() -> None:
    model = chat_model()
    for q in QUESTIONS:
        verbose_trace(model, q)

    print(
        "\n\nThree things to notice."
        "\n  1. The first question needed three tool calls in two rounds, and "
        "\n     nobody scripted that. The model worked out the sequence."
        "\n  2. Two of those calls came back in a single reply. A model can ask "
        "\n     for several things at once, which is why your loop iterates over "
        "\n     reply.tool_calls rather than taking the first."
        "\n  3. The last question called no tools at all — and was refused, "
        "\n     because the system prompt says this agent answers about Amrita "
        "\n     courses. Scope is set in the system message, not in the loop."
    )


if __name__ == "__main__":
    main()
