"""A chat model that says exactly what the test tells it to say.

Every graded test in this workshop runs against `ScriptedChatModel`, never
against the real server. That is a deliberate design decision and the reason
the tests are worth anything.

A language model is free to answer the same prompt two different ways. If the
tests called the real model, a correct solution would sometimes fail and an
incorrect one would sometimes pass, and nobody could tell which had happened.
By scripting the replies, a test failure means one thing only: the pattern was
wired up wrongly. It also means the tests still pass on a laptop with no
network, on a train, or after the workshop is over.

The real model is still very much part of the day. Each block has a `demo.py`
that runs the same code against the School's server, which is where you watch
it actually think. The tests check the wiring; the demo shows the behaviour.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field, PrivateAttr


class ScriptExhausted(AssertionError):
    """The model was called more times than the script allows.

    Almost always an agent loop that does not stop when it should.
    """


class ScriptedChatModel(BaseChatModel):
    """Returns queued replies in order and records everything it was sent.

    `script` is a list of `AIMessage`, consumed one per call. `received` holds
    the message list passed on each call, so a test can assert not just the
    result but that the tool's output was actually fed back to the model.
    """

    script: list[AIMessage] = Field(default_factory=list)
    received: list[list[BaseMessage]] = Field(default_factory=list)
    bound_tools: list[dict] = Field(default_factory=list)

    _cursor: int = PrivateAttr(default=0)

    @property
    def _llm_type(self) -> str:
        return "scripted"

    @property
    def call_count(self) -> int:
        return self._cursor

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self.received.append(list(messages))
        if self._cursor >= len(self.script):
            raise ScriptExhausted(
                f"The model was called {self._cursor + 1} times but the script "
                f"has only {len(self.script)} replies.\n"
                f"This usually means your loop never reaches its stopping "
                f"condition — check that you stop when the reply has no tool calls."
            )
        message = self.script[self._cursor]
        self._cursor += 1
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(
        self,
        tools: Sequence[Any],
        **kwargs: Any,
    ) -> Runnable[Any, BaseMessage]:
        """Record what was bound, then behave like any tool-bound chat model.

        Recording matters: several tests check that the participant actually
        gave the model its tools, which is the single most common omission.
        """
        converted = [convert_to_openai_tool(t) for t in tools]
        self.bound_tools.extend(converted)
        return self.bind(tools=converted, **kwargs)

    @property
    def bound_tool_names(self) -> list[str]:
        return [t["function"]["name"] for t in self.bound_tools]


class DeterministicEmbeddings(Embeddings):
    """Word-hashing embeddings. No model, no network, same answer every time.

    Retrieval tests need vectors, but they do not need *good* vectors: they need
    two passages about the same thing to land closer together than two passages
    about different things, identically on every machine. Hashing each word into
    a fixed number of buckets does that in a few lines and runs instantly, which
    keeps block 4's tests as offline as the other five.

    The real embedding model is what `demo.py` uses. This is for the tests.
    """

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def _vector(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        words = re.findall(r"[a-z0-9]+", text.lower())
        for word in words:
            # blake2b keeps this stable across processes; Python's hash() is
            # salted per interpreter and would make the tests irreproducible.
            bucket = int.from_bytes(
                hashlib.blake2b(word.encode(), digest_size=4).digest(), "big"
            ) % self.dimensions
            vec[bucket] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec] if norm else vec

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


def says(text: str) -> AIMessage:
    """A plain reply with no tool calls."""
    return AIMessage(content=text)


def calls_tool(name: str, args: dict, *, call_id: str = "call_1", content: str = "") -> AIMessage:
    """A reply asking for one tool to be run."""
    return AIMessage(
        content=content,
        tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}],
    )
