"""Shared runtime for the Agentic AI hands-on workshop.

Amrita School of AI, Coimbatore.

Three things live here so that no exercise has to repeat them:

    chat_model()        the School's self-hosted chat model
    embeddings()        the School's self-hosted embedding model
    ScriptedChatModel   the deterministic stand-in the graded tests use
"""

from .config import EndpointNotFound, chat_base_url, describe, embed_base_url
from .models import chat_model, embeddings
from .testing import (
    DeterministicEmbeddings,
    ScriptedChatModel,
    ScriptExhausted,
    calls_tool,
    says,
)

__all__ = [
    "chat_model",
    "embeddings",
    "ScriptedChatModel",
    "ScriptExhausted",
    "DeterministicEmbeddings",
    "says",
    "calls_tool",
    "chat_base_url",
    "embed_base_url",
    "describe",
    "EndpointNotFound",
]
