"""Block 1 — Tool Use.

Fill in the four TODOs. The scaffolding is written; you are writing the loop.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

SYSTEM = (
    "You answer questions about Amrita courses. "
    "You have tools. Use them rather than guessing: you do not know credit "
    "values, and you are unreliable at arithmetic. "
    "When you have everything you need, answer in one sentence."
)


class StepBudgetExceeded(RuntimeError):
    """The loop ran max_steps times without the model producing a final answer."""


def run_agent(
    model: BaseChatModel,
    question: str,
    tools: list[BaseTool],
    max_steps: int = 6,
) -> str:
    """Answer `question`, calling `tools` as often as the model asks.

    Returns the model's final text answer — the first reply that asks for no
    further tools.
    """
    # A name -> tool lookup, so a requested tool name can be dispatched.
    by_name = {t.name: t for t in tools}

    # TODO 1
    # Tell the model which tools exist. Without this the model has no idea it
    # can call anything and will simply guess at the answer.
    #
    #   bound = model.bind_tools(tools)
    bound = None  # replace this

    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=question)]

    for _ in range(max_steps):
        reply = bound.invoke(messages)
        messages.append(reply)

        # TODO 2
        # The stopping condition. If the reply asks for no tools, it IS the
        # final answer: return its text.
        #
        # A reply's requests are in `reply.tool_calls`, a list. Empty list
        # means no tools were requested.

        for call in reply.tool_calls:
            # TODO 3
            # Dispatch. `call` is a dict with "name", "args" and "id".
            # Look the tool up in `by_name` and run it with:
            #
            #   result = by_name[call["name"]].invoke(call["args"])
            #
            # If the model asks for a tool that does not exist, do not crash —
            # send back a message saying so, and let it try again.
            result = None  # replace this

            # TODO 4
            # Feed the result back. The tool_call_id must be the id from THIS
            # call, so the model can match answer to question:
            #
            #   messages.append(ToolMessage(content=str(result),
            #                               tool_call_id=call["id"]))
            pass

    raise StepBudgetExceeded(
        f"The model still wanted tools after {max_steps} steps. "
        f"Either the question needs a bigger budget, or a tool keeps failing "
        f"and the model keeps retrying it."
    )
