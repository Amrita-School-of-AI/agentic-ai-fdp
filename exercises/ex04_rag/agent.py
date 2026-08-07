"""Block 4 — Knowledge Retrieval (RAG).

Ground the model in documents it was never trained on. Fill in the four TODOs.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

CORPUS_DIR = Path(__file__).resolve().parents[2] / "corpus"

ANSWER = (
    "Answer the question using only the context provided.\n"
    "The context is extracted from Amrita curriculum documents.\n"
    "If the context does not contain the answer, say exactly: "
    "I cannot find that in the documents.\n"
    "Do not use anything you know outside the context. Cite the source file "
    "name for each fact you use."
)


def load_corpus(corpus_dir: Path = CORPUS_DIR) -> list[Document]:
    """Read every .txt file in the corpus directory. Provided for you."""
    docs = []
    for path in sorted(corpus_dir.glob("*.txt")):
        docs.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.name},
            )
        )
    if not docs:
        raise FileNotFoundError(f"No .txt files in {corpus_dir}")
    return docs


def split(docs: list[Document]) -> list[Document]:
    """Cut the documents into retrievable chunks.

    Chunk size is the whole game. Too large and every chunk contains several
    unrelated topics, so the model is handed noise along with the answer. Too
    small and a chunk no longer contains a complete thought — you retrieve half
    a sentence about credits and the number is in the next chunk.

    The overlap exists because the cut point is arbitrary. Without it, a fact
    sitting exactly on a boundary is split across two chunks and found in
    neither.
    """
    # TODO 1
    # Build a RecursiveCharacterTextSplitter with chunk_size=800 and
    # chunk_overlap=120, then split `docs` with it and return the result.
    #
    #   splitter = RecursiveCharacterTextSplitter(
    #       chunk_size=800, chunk_overlap=120)
    #   return splitter.split_documents(docs)
    raise NotImplementedError("TODO 1: split the documents into chunks")


def build_index(chunks: list[Document], embeddings: Embeddings) -> FAISS:
    """Embed every chunk and put it in a searchable index.

    This is the step people imagine is complicated. It is one call. Each chunk
    becomes a vector; searching means finding the vectors nearest the question's
    vector.
    """
    # TODO 2
    # Return FAISS.from_documents(chunks, embeddings)
    raise NotImplementedError("TODO 2: build the vector index")


def retrieve(index: FAISS, question: str, k: int = 4) -> list[Document]:
    """Fetch the k chunks closest to the question."""
    # TODO 3
    # Use the index's similarity search to return the k nearest chunks.
    #
    #   return index.similarity_search(question, k=k)
    raise NotImplementedError("TODO 3: retrieve the nearest chunks")


def format_context(chunks: list[Document]) -> str:
    """Turn retrieved chunks into text for the prompt. Provided for you.

    The source name is included with each chunk so the model can cite it, and
    so that you can tell at a glance whether retrieval found the right document.
    """
    return "\n\n".join(
        f"[{c.metadata.get('source', 'unknown')}]\n{c.page_content}" for c in chunks
    )


def answer(
    model: BaseChatModel,
    index: FAISS,
    question: str,
    k: int = 4,
) -> tuple[str, list[Document]]:
    """Retrieve, then answer from what was retrieved.

    Returns (answer_text, chunks_used) — the chunks come back too, because an
    answer you cannot trace to a source is not much better than a guess.
    """
    chunks = retrieve(index, question, k=k)
    context = format_context(chunks)

    # TODO 4
    # Ask the model, using ANSWER as the system message. The human message must
    # contain BOTH the context and the question — the model has no other way to
    # see the documents.
    #
    # Return (answer_text, chunks).
    raise NotImplementedError("TODO 4: answer the question from the retrieved context")
