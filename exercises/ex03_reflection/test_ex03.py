"""Tests for block 3 — Reflection."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_fdp import ScriptedChatModel, says

from .agent import CRITIC, DRAFT, reflect


def test_approved_on_the_first_critique_stops_there():
    model = ScriptedChatModel(script=[says("the first draft"), says("APPROVED")])

    result = reflect(model, "write something")

    assert result.approved is True
    assert result.final == "the first draft"
    assert result.rounds == 1
    assert model.call_count == 2, (
        "Draft, then critique, then stop. Revising an approved draft is two "
        f"wasted calls; the model was called {model.call_count} times."
    )


def test_one_revision_then_approval():
    model = ScriptedChatModel(
        script=[
            says("draft one"),
            says("- too vague\n- no example"),
            says("draft two, now with an example"),
            says("APPROVED"),
        ]
    )

    result = reflect(model, "write something")

    assert result.approved is True
    assert result.final == "draft two, now with an example", (
        "The final text must be the revised draft, not the original."
    )
    assert result.drafts == ["draft one", "draft two, now with an example"]
    assert len(result.critiques) == 2
    assert result.rounds == 2


def test_the_critic_sees_both_the_brief_and_the_draft():
    model = ScriptedChatModel(script=[says("THE-DRAFT"), says("APPROVED")])

    reflect(model, "THE-BRIEF")

    critic_call = model.received[1]
    system = [m for m in critic_call if isinstance(m, SystemMessage)]
    human = [m for m in critic_call if isinstance(m, HumanMessage)]

    assert system[0].content == CRITIC, "The critique step must use the CRITIC prompt."
    assert "THE-DRAFT" in human[0].content, "The critic was not shown the draft."
    assert "THE-BRIEF" in human[0].content, (
        "The critic was not shown the brief. It cannot judge whether text meets "
        "a brief it has never seen."
    )


def test_the_reviser_sees_the_critique():
    model = ScriptedChatModel(
        script=[
            says("draft one"),
            says("CRITIQUE-TEXT-HERE"),
            says("draft two"),
            says("APPROVED"),
        ]
    )

    reflect(model, "brief")

    revise_call = model.received[2]
    human = [m for m in revise_call if isinstance(m, HumanMessage)]
    assert "CRITIQUE-TEXT-HERE" in human[0].content, (
        "The revision step did not receive the critique. Without it the model "
        "is just rewriting at random, and nothing improves."
    )
    assert "draft one" in human[0].content, (
        "The revision step did not receive the draft it is meant to revise."
    )


def test_a_critic_that_never_approves_still_terminates():
    """The failure mode that hangs a live demo."""
    model = ScriptedChatModel(
        script=[says("draft")] + [says("- still wrong"), says("another draft")] * 5
    )

    result = reflect(model, "brief", max_rounds=2)

    assert result.approved is False
    assert result.rounds == 2, f"max_rounds was 2, but {result.rounds} rounds ran."
    assert model.call_count == 5, (
        "One draft, then two rounds of (critique, revise) — five calls. "
        f"Got {model.call_count}."
    )


def test_an_unapproved_run_returns_the_most_revised_draft():
    model = ScriptedChatModel(
        script=[
            says("draft one"),
            says("- wrong"),
            says("draft two"),
            says("- still wrong"),
            says("draft three"),
        ]
    )

    result = reflect(model, "brief", max_rounds=2)

    assert result.final == "draft three", (
        "When the rounds run out, return the latest revision — it is the best "
        f"version you have. Got {result.final!r}."
    )


def test_approval_survives_a_chatty_critic():
    """Told to reply with one word, models still add pleasantries."""
    for reply in ("APPROVED", "APPROVED.", "This is APPROVED - well done!"):
        model = ScriptedChatModel(script=[says("draft"), says(reply)])
        result = reflect(model, "brief")
        assert result.approved is True, (
            f"The critique {reply!r} is an approval. Test for the word appearing "
            f"in the reply, not for equality with it."
        )


def test_the_first_draft_uses_the_draft_prompt():
    model = ScriptedChatModel(script=[says("d"), says("APPROVED")])

    reflect(model, "brief")

    system = [m for m in model.received[0] if isinstance(m, SystemMessage)]
    assert system[0].content == DRAFT
