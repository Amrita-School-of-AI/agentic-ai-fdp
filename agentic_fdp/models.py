"""The two factories every exercise uses to reach the School's model server.

Exercises never construct a model directly. They call `chat_model()`, which
means one change here re-points the whole workshop at a different server, and a
participant whose laptop cannot reach the campus network can be fixed with an
environment variable rather than by editing six files.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import (
    API_KEY,
    CHAT_MODEL,
    EMBED_MODEL,
    chat_base_url,
    embed_base_url,
)


def chat_model(temperature: float = 0.0, **kwargs) -> ChatOpenAI:
    """The workshop's chat model.

    Temperature defaults to 0. Everything in this workshop is easier to reason
    about when the same prompt gives the same answer twice, and a participant
    debugging a routing decision should not be fighting sampling noise as well.
    """
    return ChatOpenAI(
        model=CHAT_MODEL,
        base_url=chat_base_url(),
        api_key=API_KEY,
        temperature=temperature,
        timeout=120,
        max_retries=2,
        **kwargs,
    )


def embeddings(**kwargs) -> OpenAIEmbeddings:
    """The workshop's embedding model, served on CPU next to the chat model.

    `check_embedding_ctx_length=False` is required, not cosmetic. Left on, the
    client tokenises text locally with OpenAI's tokeniser and posts token IDs
    instead of strings, which our server cannot interpret because it does not
    use that tokeniser.
    """
    return OpenAIEmbeddings(
        model=EMBED_MODEL,
        base_url=embed_base_url(),
        api_key=API_KEY,
        check_embedding_ctx_length=False,
        **kwargs,
    )
