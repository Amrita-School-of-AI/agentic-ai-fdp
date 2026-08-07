"""Tests for block 5 — the multi-agent capstone."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END

from agentic_fdp import ScriptedChatModel, says

from .agent import (
    MAX_STEPS,
    RESEARCHER,
    SUPERVISOR,
    WRITER,
    research_node,
    route,
    run,
    supervisor_node,
    writer_node,
)
from .corpus_search import search_corpus

QUESTION = "How many credits does the Data Science programme require?"


def _state(**over):
    base = {"question": QUESTION, "notes": [], "draft": "", "steps": 0, "next": ""}
    base.update(over)
    return base


# --- the supervisor --------------------------------------------------------


def test_supervisor_returns_the_decision_and_counts_the_step():
    model = ScriptedChatModel(script=[says("RESEARCH")])

    out = supervisor_node(_state(), model)

    assert out["next"] == "RESEARCH"
    assert out["steps"] == 1, "Every supervisor turn must increment steps."


def test_supervisor_normalises_a_messy_reply():
    for reply in ("research", "RESEARCH.", "  Research  ", "RESEARCH!"):
        model = ScriptedChatModel(script=[says(reply)])
        assert supervisor_node(_state(), model)["next"] == "RESEARCH", (
            f"{reply!r} should normalise to RESEARCH."
        )


def test_supervisor_falls_back_to_write_on_an_unrecognised_reply():
    model = ScriptedChatModel(script=[says("I am not sure what to do here")])

    assert supervisor_node(_state(), model)["next"] == "WRITE", (
        "An unrecognised decision should fall back to WRITE, so the system "
        "produces an answer instead of stalling."
    )


def test_supervisor_is_shown_the_notes_and_the_draft():
    model = ScriptedChatModel(script=[says("DONE")])

    supervisor_node(_state(notes=["NOTE-ALPHA"], draft="DRAFT-BETA"), model)

    sent = model.received[0]
    system = [m for m in sent if isinstance(m, SystemMessage)][0]
    human = [m for m in sent if isinstance(m, HumanMessage)][0]

    assert system.content == SUPERVISOR
    assert "NOTE-ALPHA" in human.content, "The supervisor cannot judge progress without the notes."
    assert "DRAFT-BETA" in human.content, "The supervisor was not shown the answer written so far."


# --- the workers -----------------------------------------------------------


def test_researcher_is_given_the_question_and_the_passages():
    model = ScriptedChatModel(script=[says("- the programme requires 65 credits")])

    out = research_node(_state(), model)

    assert out["notes"] == ["- the programme requires 65 credits"]
    assert isinstance(out["notes"], list), (
        "Notes must be returned as a list so the state merges them by "
        "concatenation. Returning a bare string replaces the history instead."
    )

    human = [m for m in model.received[0] if isinstance(m, HumanMessage)][0]
    system = [m for m in model.received[0] if isinstance(m, SystemMessage)][0]
    assert system.content == RESEARCHER
    assert QUESTION in human.content, "The researcher was not told the question."
    assert len(human.content) > len(QUESTION) + 200, (
        "The retrieved passages do not appear to be in the prompt. The "
        "researcher has no other way to see the documents."
    )


def test_writer_answers_from_the_notes():
    model = ScriptedChatModel(script=[says("It requires 65 credits.")])

    out = writer_node(_state(notes=["NOTE-ONE", "NOTE-TWO"]), model)

    assert out["draft"] == "It requires 65 credits."

    human = [m for m in model.received[0] if isinstance(m, HumanMessage)][0]
    system = [m for m in model.received[0] if isinstance(m, SystemMessage)][0]
    assert system.content == WRITER
    assert "NOTE-ONE" in human.content and "NOTE-TWO" in human.content, (
        "The writer must receive every note, not just the most recent one."
    )


# --- routing and goal monitoring -------------------------------------------


def test_route_sends_each_decision_to_the_right_place():
    assert route(_state(next="RESEARCH")) == "research"
    assert route(_state(next="WRITE")) == "write"
    assert route(_state(next="DONE")) == END


def test_route_stops_when_the_budget_is_spent():
    """The check that keeps a confused supervisor from running forever."""
    assert route(_state(next="RESEARCH", steps=MAX_STEPS)) == END, (
        f"At {MAX_STEPS} steps the run must end regardless of what the "
        f"supervisor asked for."
    )
    assert route(_state(next="RESEARCH", steps=MAX_STEPS + 3)) == END


def test_budget_is_checked_before_the_decision():
    """Order matters: checking the decision first grants one extra round."""
    assert route(_state(next="WRITE", steps=MAX_STEPS)) == END


# --- the whole system ------------------------------------------------------


def test_a_full_run_researches_then_writes_then_stops():
    model = ScriptedChatModel(
        script=[
            says("RESEARCH"),
            says("- the programme requires 65 credits"),
            says("WRITE"),
            says("The Data Science programme requires 65 credits."),
            says("DONE"),
        ]
    )

    final = run(model, QUESTION)

    assert final["draft"] == "The Data Science programme requires 65 credits."
    assert final["notes"] == ["- the programme requires 65 credits"]
    assert final["steps"] == 3, (
        f"Three supervisor turns: research, write, done. Got {final['steps']}."
    )


def test_a_supervisor_that_never_stops_is_stopped_anyway():
    """The failure this whole block is really about."""
    model = ScriptedChatModel(script=[says("RESEARCH"), says("- a fact")] * 20)

    final = run(model, QUESTION)

    assert final["steps"] <= MAX_STEPS, (
        f"The run reached {final['steps']} steps with a budget of {MAX_STEPS}. "
        f"Without a working budget check this would not terminate at all."
    )


def test_writing_immediately_is_allowed():
    model = ScriptedChatModel(
        script=[says("WRITE"), says("I cannot find that in the documents."), says("DONE")]
    )

    final = run(model, QUESTION)

    assert final["draft"] == "I cannot find that in the documents."
    assert final["notes"] == []


# --- the provided search ---------------------------------------------------


def test_provided_search_finds_something_relevant():
    hits = search_corpus("data science programme credits", k=3)

    assert hits, "The keyword search returned nothing for an obviously covered topic."
    assert all(len(passage) > 100 for _, passage in hits)


def test_provided_search_handles_a_query_with_no_content_words():
    assert search_corpus("the and of", k=3) == []
