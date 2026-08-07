"""Tests for block 2 — Prompt Chaining and Routing."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_fdp import ScriptedChatModel, says

from .agent import ROUTER, ROUTES, chain, pick_route, route_and_answer

# --- Part A: chaining ------------------------------------------------------


def test_chain_makes_two_calls_and_returns_both_outputs():
    model = ScriptedChatModel(script=[says("- fact one\n- fact two"), says("Two Facts Found")])

    facts, headline = chain(model, "some long text")

    assert facts == "- fact one\n- fact two"
    assert headline == "Two Facts Found"
    assert model.call_count == 2, (
        f"A chain of two stages is two model calls; this made {model.call_count}."
    )


def test_second_stage_reads_the_first_stages_output():
    """The defining property of a chain. Without this it is just two calls."""
    model = ScriptedChatModel(script=[says("THE-EXTRACTED-FACTS"), says("headline")])

    chain(model, "the original input text")

    second_call = model.received[1]
    human = [m for m in second_call if isinstance(m, HumanMessage)]
    assert human, "The second call sent no HumanMessage."
    assert "THE-EXTRACTED-FACTS" in human[0].content, (
        "The second call did not receive the first call's output. A chain feeds "
        "stage one's result into stage two; passing the original text again "
        "makes it two independent calls, not a chain. "
        f"Second call actually got: {human[0].content!r}"
    )


def test_each_stage_uses_its_own_system_message():
    model = ScriptedChatModel(script=[says("facts"), says("headline")])

    chain(model, "text")

    first_system = [m for m in model.received[0] if isinstance(m, SystemMessage)]
    second_system = [m for m in model.received[1] if isinstance(m, SystemMessage)]
    assert first_system and second_system, "Both stages need a system message."
    assert first_system[0].content != second_system[0].content, (
        "Both stages used the same system message, so both did the same job."
    )


# --- Part B: routing -------------------------------------------------------


def test_pick_route_returns_the_models_choice():
    model = ScriptedChatModel(script=[says("policy")])

    assert pick_route(model, "How many credits is 23AID304?") == "policy"


def test_pick_route_uses_the_router_prompt():
    model = ScriptedChatModel(script=[says("maths")])

    pick_route(model, "what is 2+2")

    system = [m for m in model.received[0] if isinstance(m, SystemMessage)]
    assert system and system[0].content == ROUTER, (
        "pick_route must classify using the ROUTER system message."
    )


def test_pick_route_tolerates_a_messy_reply():
    """Models add full stops and capitals however firmly you ask them not to."""
    for reply in ("Maths", "maths.", "  MATHS  ", "maths!"):
        model = ScriptedChatModel(script=[says(reply)])
        assert pick_route(model, "q") == "maths", (
            f"The reply {reply!r} should still resolve to 'maths'. Strip "
            f"whitespace and punctuation, and lowercase, before comparing."
        )


def test_pick_route_falls_back_to_other_when_unrecognised():
    model = ScriptedChatModel(script=[says("I think this is about chemistry")])

    assert pick_route(model, "q") == "other", (
        "An unrecognised classification must fall back to 'other'. Raising "
        "KeyError here means one odd model reply takes down the whole system."
    )


def test_route_and_answer_uses_the_chosen_routes_system_message():
    model = ScriptedChatModel(script=[says("policy"), says("It carries 3 credits.")])

    route, answer = route_and_answer(model, "credits for 23AID304?")

    assert route == "policy"
    assert answer == "It carries 3 credits."
    assert model.call_count == 2, "One call to classify, one to answer."

    answering_system = [m for m in model.received[1] if isinstance(m, SystemMessage)]
    assert answering_system[0].content == ROUTES["policy"], (
        "The answering call must use the chosen route's system message. Using "
        "the same generic prompt for every route makes the router pointless."
    )


def test_a_different_route_gets_a_different_system_message():
    model = ScriptedChatModel(script=[says("maths"), says("4")])

    route, _ = route_and_answer(model, "what is 2+2")

    assert route == "maths"
    system = [m for m in model.received[1] if isinstance(m, SystemMessage)]
    assert system[0].content == ROUTES["maths"]
