"""Tests for block 4 — Knowledge Retrieval.

Uses DeterministicEmbeddings, not the real embedding server, so retrieval gives
the same result on every machine and the block still works offline.
"""

from __future__ import annotations

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from agentic_fdp import DeterministicEmbeddings, ScriptedChatModel, says

from .agent import (
    ANSWER,
    answer,
    build_index,
    format_context,
    load_corpus,
    retrieve,
    split,
)

# Small, obviously-separable documents. Retrieval either finds the right one or
# it does not, with no ambiguity to argue about.
DOCS = [
    Document(
        page_content=(
            "The Data Science programme requires sixty five credits in total. "
            "Students take a project in the fourth semester worth twelve credits."
        ),
        metadata={"source": "data-science.txt"},
    ),
    Document(
        page_content=(
            "The Artificial Intelligence programme covers reinforcement learning "
            "and computer vision as core subjects in the second semester."
        ),
        metadata={"source": "artificial-intelligence.txt"},
    ),
    Document(
        page_content=(
            "Laboratory safety rules require closed footwear and prohibit food "
            "and drink near the equipment at all times."
        ),
        metadata={"source": "safety.txt"},
    ),
]


@pytest.fixture
def index():
    return build_index(DOCS, DeterministicEmbeddings())


def test_split_produces_chunks_smaller_than_the_source():
    long_doc = [Document(page_content="sentence about credits. " * 400, metadata={"source": "x"})]

    chunks = split(long_doc)

    assert len(chunks) > 1, (
        "A 9000-character document must split into several chunks. Check that "
        "chunk_size is set and split_documents was actually called."
    )
    assert all(len(c.page_content) <= 1000 for c in chunks), (
        "Some chunk came back far larger than the requested chunk_size."
    )


def test_split_keeps_the_source_metadata():
    chunks = split(DOCS)

    assert all("source" in c.metadata for c in chunks), (
        "Chunks lost their source metadata. Without it the answer cannot cite "
        "which document a fact came from."
    )


def test_retrieval_finds_the_relevant_document(index):
    hits = retrieve(index, "how many credits does the data science programme need", k=1)

    assert hits[0].metadata["source"] == "data-science.txt", (
        f"Retrieval returned {hits[0].metadata['source']} for a question about "
        f"data science credits."
    )


def test_retrieval_discriminates_between_similar_documents(index):
    hits = retrieve(index, "reinforcement learning and computer vision", k=1)

    assert hits[0].metadata["source"] == "artificial-intelligence.txt"


def test_retrieval_respects_k(index):
    assert len(retrieve(index, "credits", k=2)) == 2
    assert len(retrieve(index, "credits", k=3)) == 3


def test_answer_puts_the_retrieved_text_in_the_prompt(index):
    model = ScriptedChatModel(script=[says("Sixty five credits.")])

    text, chunks = answer(model, index, "how many credits for data science", k=1)

    assert text == "Sixty five credits."
    assert chunks, "The chunks used must be returned alongside the answer."

    sent = model.received[0]
    human = [m for m in sent if isinstance(m, HumanMessage)][0]
    assert "sixty five credits" in human.content.lower(), (
        "The retrieved passage never reached the model. Retrieval that is not "
        "put into the prompt does nothing at all — the model still answers from "
        "memory. This is the single most common way RAG is got wrong."
    )
    assert "how many credits for data science" in human.content, (
        "The question itself must be in the prompt too, not only the context."
    )


def test_answer_uses_the_grounding_system_message(index):
    model = ScriptedChatModel(script=[says("x")])

    answer(model, index, "q", k=1)

    system = [m for m in model.received[0] if isinstance(m, SystemMessage)]
    assert system and system[0].content == ANSWER, (
        "The ANSWER system message is what confines the model to the context. "
        "Without it the model happily answers from training data and you have "
        "retrieval with none of the grounding."
    )


def test_format_context_labels_each_chunk_with_its_source():
    out = format_context(DOCS)

    assert "data-science.txt" in out
    assert "safety.txt" in out


def test_the_real_corpus_loads():
    docs = load_corpus()

    assert len(docs) >= 2, "Expected at least the two curriculum documents."
    assert all(len(d.page_content) > 1000 for d in docs)
    assert all(d.metadata["source"].endswith(".txt") for d in docs)


def test_the_real_corpus_splits_into_a_sensible_number_of_chunks():
    chunks = split(load_corpus())

    assert 200 < len(chunks) < 2000, (
        f"{len(chunks)} chunks from roughly 350 KB of text looks wrong. "
        f"Check chunk_size — 800 characters gives a few hundred."
    )
