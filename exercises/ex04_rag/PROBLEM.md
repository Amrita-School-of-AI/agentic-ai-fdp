# Block 4 — Knowledge Retrieval (RAG)

**60 minutes.** Give the model documents it was never trained on.
Gulli, *Agentic Design Patterns*, chapter 14.

## The problem, again

Block 1 solved "the model does not know our credit values" by giving it a
function to call. That works when the knowledge is a lookup with a clean key.

It does not work for a 74-page curriculum document. There is no `get_answer()`
function for "what does the fourth-semester project involve". The knowledge is
prose, and the question could be about any part of it.

## The move

Do not give the model the document. Give it the *four paragraphs of the document
that relate to the question*.

```
                    ┌──────────── indexed once, up front ────────────┐
documents ──▶ split into chunks ──▶ embed each chunk ──▶ vector index
                                                              │
question ──▶ embed the question ──▶ find nearest chunks ◀─────┘
                                          │
                                          ▼
              [system: answer only from this context] + chunks + question ──▶ model
```

"Embed" means turn text into a list of numbers positioned so that text about
similar things lands nearby. Finding relevant chunks then becomes finding
nearby points, which computers are extremely good at.

## What to build

Four TODOs in `agent.py`: split, index, retrieve, and — the one that matters —
put what you retrieved into the prompt.

## Where this goes wrong

**Retrieving and then not using it.** The commonest RAG bug by a wide margin.
You build a beautiful index, retrieve four perfect chunks, and then send the
model the bare question. It answers from training data, sounds confident, and
nothing in the output tells you the retrieval was ignored.
`test_answer_puts_the_retrieved_text_in_the_prompt` exists for this.

**Chunk size.** 800 characters here, and the number is not sacred. Too big and
each chunk mixes several topics, so you hand the model noise. Too small and a
chunk stops containing a complete thought — you retrieve "the programme
requires" and the number lives in the next chunk. Change it in `split()` and
watch the demo's answers change. That experiment is worth more than any advice
about the right value.

**Overlap.** The cut points are arbitrary. Without overlap, a fact sitting
exactly on a boundary is halved and found by neither chunk.

## Two documents, on purpose

The corpus holds both the M.Tech Data Science and the M.Tech AI curricula. They
share a lot of vocabulary, so a lazy retriever pulls from the wrong one. The
demo asks questions answerable from exactly one — check the citations it gives
you.

## Done when

```bash
./selfcheck ex04
uv run python -m exercises.ex04_rag.demo
```

The demo prints which chunks were retrieved before it prints the answer. Read
the chunks first, then decide whether the answer is grounded or invented. Doing
that by hand a few times is how you develop a nose for it.

## A note on the tests

These tests use a small offline embedding stand-in rather than the School's
embedding server, so they work with the wifi off and give identical results on
every laptop. The demo uses the real embedding model. Chunks retrieved by the
two will differ, and that is expected.
