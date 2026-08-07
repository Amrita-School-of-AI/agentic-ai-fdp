# Block 3 — Reflection

**45 minutes.** The model marks its own work.
Gulli, *Agentic Design Patterns*, chapter 4.

## The idea

A model's first answer is a first draft. Ask the *same model* to review that
draft against the brief and it will find real faults — vagueness, a missing
example, an unanswered part of the question. Feed the critique back and the
second draft is usually better.

This is strange the first time you see it. If the model could write the better
version, why did it not write it first? Because writing and judging are
different tasks, and a model doing one is not doing the other. Given a finished
text and asked "what is wrong with this", it attends to different things than it
did while generating.

```
brief ──▶ draft ──▶ critique ──▶ approved? ──yes──▶ final
                        ▲             │
                        └── revise ◀──┘ no
```

## What to build

`reflect(model, brief, max_rounds=3)` in `agent.py`, returning a `Reflection`
holding the final text, every draft, and every critique.

Three TODOs: run the critique, detect approval, revise.

## Two things the tests are strict about

**Stopping.** A critic that keeps finding faults must not loop forever. When the
rounds run out, return the most revised draft — it is the best version you have,
and raising an exception throws away real work.

**Detecting approval.** You tell the critic to reply with exactly `APPROVED`. It
will reply `APPROVED.` or `This is APPROVED - well done!`. Test for the word
appearing in the reply, not for the reply equalling it. Anything else and your
loop silently runs the full three rounds every single time, paying triple for
nothing.

## What it costs

Reflection turns one call into three or five. That is real money and real
latency, and it is not always worth it. Run the demo and read the drafts: some
briefs improve enormously between round one and round two, and some barely
change. Knowing which is which for your own use case is the engineering
judgement here — the pattern is easy, deciding when to spend it is not.

## Done when

```bash
./selfcheck ex03
uv run python -m exercises.ex03_reflection.demo
```

The demo prints every draft and every critique. Read them. That trail is the
only evidence that the extra calls bought you anything.
