"""Tests for block 1 — Tool Use.

Scripted model throughout: the replies are fixed, so a failure means the loop is
wrong, never that the model had an off day.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import ToolMessage

from agentic_fdp import ScriptedChatModel, calls_tool, says

from .agent import StepBudgetExceeded, run_agent
from .tools import ALL_TOOLS, calculator, course_credits


def test_returns_immediately_when_no_tools_are_requested():
    model = ScriptedChatModel(script=[says("42 credits.")])

    answer = run_agent(model, "anything", ALL_TOOLS)

    assert answer == "42 credits."
    assert model.call_count == 1, (
        "The model asked for no tools, so the loop should have stopped after "
        f"one call. It made {model.call_count}."
    )


def test_tools_are_given_to_the_model():
    model = ScriptedChatModel(script=[says("done")])

    run_agent(model, "anything", ALL_TOOLS)

    assert sorted(model.bound_tool_names) == ["calculator", "course_credits"], (
        "The model was never told which tools exist. Without bind_tools it can "
        f"only guess. Bound: {model.bound_tool_names}"
    )


def test_a_requested_tool_actually_runs_and_the_result_goes_back():
    model = ScriptedChatModel(
        script=[
            calls_tool("course_credits", {"code": "23AID304"}),
            says("It carries 3 credits."),
        ]
    )

    answer = run_agent(model, "credits for 23AID304?", ALL_TOOLS)

    assert answer == "It carries 3 credits."

    second_turn = model.received[1]
    tool_messages = [m for m in second_turn if isinstance(m, ToolMessage)]
    assert tool_messages, (
        "The tool result never reached the model. After running a tool you must "
        "append a ToolMessage to the message list."
    )
    assert "3 credits" in tool_messages[0].content, (
        f"The ToolMessage did not carry the tool's output. It said: "
        f"{tool_messages[0].content!r}"
    )


def test_tool_message_carries_the_matching_call_id():
    model = ScriptedChatModel(
        script=[
            calls_tool("course_credits", {"code": "23AID304"}, call_id="abc123"),
            says("done"),
        ]
    )

    run_agent(model, "q", ALL_TOOLS)

    tool_messages = [m for m in model.received[1] if isinstance(m, ToolMessage)]
    assert tool_messages[0].tool_call_id == "abc123", (
        "The ToolMessage must carry the id of the call it answers. The model "
        "matches results to requests by that id, and invents nothing. Got "
        f"{tool_messages[0].tool_call_id!r}, expected 'abc123'."
    )


def test_several_tools_in_one_reply_all_run():
    """The model may ask for several things at once. All of them must run."""
    both = calls_tool("course_credits", {"code": "23AID304"}, call_id="a")
    both.tool_calls.append(
        {"name": "course_credits", "args": {"code": "24AIM332"}, "id": "b", "type": "tool_call"}
    )
    model = ScriptedChatModel(script=[both, says("Seven in total.")])

    answer = run_agent(model, "23AID304 and 24AIM332 together?", ALL_TOOLS)

    assert answer == "Seven in total."
    tool_messages = [m for m in model.received[1] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 2, (
        f"Two tools were requested but {len(tool_messages)} results came back. "
        "Loop over every entry in reply.tool_calls, not just the first."
    )
    assert {m.tool_call_id for m in tool_messages} == {"a", "b"}


def test_a_multi_step_conversation_reaches_the_answer():
    model = ScriptedChatModel(
        script=[
            calls_tool("course_credits", {"code": "23AID304"}, call_id="1"),
            calls_tool("calculator", {"expression": "3 + 4"}, call_id="2"),
            says("Seven credits in total."),
        ]
    )

    assert run_agent(model, "q", ALL_TOOLS) == "Seven credits in total."
    assert model.call_count == 3


def test_step_budget_is_respected():
    """A model that never stops asking must not loop forever."""
    model = ScriptedChatModel(
        script=[calls_tool("course_credits", {"code": "23AID304"}, call_id=str(i)) for i in range(10)]
    )

    with pytest.raises(StepBudgetExceeded):
        run_agent(model, "q", ALL_TOOLS, max_steps=3)

    assert model.call_count == 3, (
        f"max_steps was 3 but the model was called {model.call_count} times."
    )


def test_an_unknown_tool_does_not_crash_the_agent():
    model = ScriptedChatModel(
        script=[
            calls_tool("no_such_tool", {"x": 1}, call_id="z"),
            says("Sorry, I cannot do that."),
        ]
    )

    answer = run_agent(model, "q", ALL_TOOLS)

    assert answer == "Sorry, I cannot do that.", (
        "When the model asks for a tool that does not exist, report it back as "
        "a ToolMessage and let the model recover. Do not raise KeyError."
    )


# The provided tools are not the participant's work, but a broken tool would
# make the exercise impossible to debug, so they are checked too.


def test_provided_tools_behave():
    assert "3 credits" in course_credits.invoke({"code": "23AID304"})
    assert "not in the catalogue" in course_credits.invoke({"code": "ZZ999"})
    assert calculator.invoke({"expression": "3 + 4"}) == "7"
    assert "Could not evaluate" in calculator.invoke({"expression": "__import__('os')"})
