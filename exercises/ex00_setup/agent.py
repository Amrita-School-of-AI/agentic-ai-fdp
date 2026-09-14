"""Block 0 — reference solution. Instructor copy.

Not published to the participant repository.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


def ask(model: BaseChatModel, question: str) -> str:
    reply = model.invoke([HumanMessage(content=question)])
    return reply.content


def ask_as(model: BaseChatModel, role: str, question: str) -> str:
    reply = model.invoke(
        [
            SystemMessage(content=role),
            HumanMessage(content=question),
        ]
    )
    return reply.content
