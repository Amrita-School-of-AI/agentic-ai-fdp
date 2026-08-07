"""Tests for block 0.

These run against a scripted model, never the server, so they give the same
answer on every laptop and work with the wifi off.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_fdp import ScriptedChatModel, says

from .agent import ask, ask_as


def test_ask_returns_the_reply_text():
    model = ScriptedChatModel(script=[says("Coimbatore")])

    assert ask(model, "Where is Amrita School of AI?") == "Coimbatore"


def test_ask_sends_the_question_as_a_human_message():
    model = ScriptedChatModel(script=[says("ok")])

    ask(model, "the question I asked")

    sent = model.received[0]
    assert any(
        isinstance(m, HumanMessage) and "the question I asked" in m.content for m in sent
    ), (
        "The question did not reach the model as a HumanMessage. "
        f"What was sent: {[type(m).__name__ for m in sent]}"
    )


def test_ask_as_puts_the_system_message_first():
    model = ScriptedChatModel(script=[says("ok")])

    ask_as(model, "You are a strict examiner.", "Is 2+2 equal to 4?")

    sent = model.received[0]
    assert len(sent) == 2, (
        f"Expected exactly two messages, a system message then the question, "
        f"but {len(sent)} were sent."
    )
    assert isinstance(sent[0], SystemMessage), (
        "The first message must be the SystemMessage. A system message placed "
        "after the question is generally ignored."
    )
    assert "strict examiner" in sent[0].content
    assert isinstance(sent[1], HumanMessage)


def test_ask_as_returns_the_reply_text():
    model = ScriptedChatModel(script=[says("Yes.")])

    assert ask_as(model, "You answer in one word.", "Is 2+2 equal to 4?") == "Yes."


def test_each_call_invokes_the_model_exactly_once():
    model = ScriptedChatModel(script=[says("a"), says("b")])

    ask(model, "first")
    ask_as(model, "role", "second")

    assert model.call_count == 2, (
        f"The model should be called once per question, but it was called "
        f"{model.call_count} times."
    )
