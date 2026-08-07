# Block 5 — Multi-Agent, with goal monitoring

**75 minutes.** The capstone. Everything from the day, in one system.
Gulli, *Agentic Design Patterns*, chapters 7 and 11.

## Why more than one agent

A single agent with six tools and a long system prompt degrades. The prompt
grows to cover every case, the instructions start contradicting each other, and
behaviour becomes hard to predict and harder to change.

Splitting the work into agents with narrow jobs is the same move as splitting a
long function: each part is small enough to reason about, and you can change one
without breaking the others.

Here: a **researcher** that only finds facts, a **writer** that only writes from
facts it is given, and a **supervisor** that decides which of them acts next.

```
   START ─▶ supervisor ─┬─▶ research ─┐
                        ├─▶ write ────┤
                        └─▶ END       │
                             ▲        │
                             └────────┘
                    (workers report back)
```

Both workers return to the supervisor. That is what makes this a supervised team
rather than a fixed pipeline: after each piece of work someone decides again
what should happen next, so the same graph handles "needs three rounds of
research" and "answerable straight away".

## The part that is really the lesson

**Nothing here stops on its own.**

The supervisor can keep saying RESEARCH. The researcher will keep researching.
No exception is raised, no test fails, nothing looks broken. The system simply
runs, and on a metered API it runs up a bill while you are at lunch.

So the state carries a `steps` counter, and `route` checks it **before** it looks
at the supervisor's decision. That is goal monitoring: an explicit, external
condition under which the system stops, which does not depend on the model
choosing to stop.

Check the budget first, not second. Checking the decision first grants one extra
round every single time, which is the kind of bug that only shows up on the
invoice.

## What to build

Four TODOs: the supervisor's decision, the researcher's note, the writer's
answer, and `route`. The graph wiring at the bottom of `agent.py` is written for
you — read it before you start, because it tells you what each node must return.

## Where the day's other patterns show up

- **Routing** (block 2) — the supervisor is a router, with the same
  normalise-and-fall-back problem, for the same reason.
- **Tool use** (block 1) — the researcher calls `search_corpus`, and its findings
  come back as state rather than as a `ToolMessage`.
- **Retrieval** (block 4) — same idea, keyword scoring instead of embeddings.
  Deliberate: the last block of the day should not be able to fail because a
  server is busy. Retrieval does not have to mean vectors.
- **Reflection** (block 3) — the supervisor judging whether the draft answers the
  question is a critique step by another name.

## Done when

```bash
./selfcheck ex05
uv run python -m exercises.ex05_capstone.demo
```

The demo prints every supervisor decision. Watch it choose, and notice that the
sequence differs between questions — that is the difference between a team and a
pipeline.

## If you finish early

Try any of these; none needs new concepts, all change the behaviour visibly:

1. Add a **reviewer** agent that can send a draft back for another round. You
   now have reflection inside a multi-agent system, and a much better reason for
   the step budget to exist.
2. Make the researcher write its own **search query** instead of reusing the
   question verbatim. Ask whether it retrieves better passages.
3. Drop `MAX_STEPS` to 2 and watch a good system produce a bad answer. Budgets
   are a trade, not a free safety net.
