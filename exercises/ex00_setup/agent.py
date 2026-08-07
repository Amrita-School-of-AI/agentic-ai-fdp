"""Block 0 — your first model call.

Fill in the two TODOs. Everything else is written for you.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


def ask(model: BaseChatModel, question: str) -> str:
    """Send one question to the model and return its reply as plain text.

    A chat model takes a *list of messages*, not a string. Wrap the question in
    a HumanMessage, put it in a list, and invoke.

    The reply is an AIMessage. Its text is in `.content`.
    """
    # TODO 1
    # Build the message list and invoke the model, then return the reply text.
    #
    #   messages = [HumanMessage(content=question)]
    #   reply = model.invoke(messages)
    #   return reply.content
    #
    # Write those three lines yourself, then delete this comment and the
    # raise below.
    raise NotImplementedError("TODO 1: send the question and return the reply text")


def ask_as(model: BaseChatModel, role: str, question: str) -> str:
    """Same, but tell the model who to be first.

    `role` is a sentence such as "You are a strict examiner who answers in one
    line." It goes in a SystemMessage, which must come *before* the question.
    """
    # TODO 2
    # Build a two-message list — the system message first, then the question —
    # invoke, and return the reply text.
    raise NotImplementedError("TODO 2: put a SystemMessage in front of the question")
