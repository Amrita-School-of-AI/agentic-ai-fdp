# Block 2 — Prompt Chaining and Routing

**45 minutes.** Two patterns, both small, both everywhere.
Gulli, *Agentic Design Patterns*, chapters 1 and 2.

---

## Part A — Prompt Chaining (chapter 1)

Ask a model to "read this and give me a headline" and it does two jobs at once:
work out what matters, then compress it. It does both a bit worse than it would
do either alone.

Chaining splits them:

```
text ──▶ [extract the facts] ──▶ facts ──▶ [headline these facts] ──▶ headline
```

Each call now has one instruction. You also get the intermediate result, which
means when the headline is wrong you can see *why*: were the facts wrong, or was
the compression wrong? A single call gives you no such handle.

**Build** `chain(model, text)`, returning `(facts, headline)`.

The test that matters is `test_second_stage_reads_the_first_stages_output`. If
stage two re-reads the original text instead of stage one's output, you have
written two independent calls, not a chain.

---

## Part B — Routing (chapter 2)

One assistant that handles everything is mediocre at all of it. The fix is to
ask, first, *what kind of question is this*, and then hand it to a handler built
for that kind.

```
                    ┌─▶ maths tutor
question ──▶ router ├─▶ policy clerk
                    └─▶ general assistant
```

Notice in `ROUTES` that the three handlers differ **only by system message**.
Same model, same code path, three behaviours. That is the cheapest specialisation
available to you, and it is why block 0 spent time on system messages.

**Build** `pick_route(model, question)` and `route_and_answer(model, question)`.

### The part that bites

You will ask for one word. You will get `"Maths."` or `"  MATHS  "` or, one time
in fifty, `"I think this is about chemistry"`. A router that does
`ROUTES[reply]` raises `KeyError` in front of the room.

So: normalise the reply, and fall back to `other` when it is not recognised.
Both are tested. This is the single most common way a routing agent fails in
production, and it has nothing to do with AI — it is ordinary defensive coding
against an unreliable input.

---

## Done when

```bash
./selfcheck ex02
uv run python -m exercises.ex02_chaining_routing.demo
```

In the demo, watch the middle step of the chain print. That intermediate value
is the whole argument for chaining: you can inspect it, log it, cache it, or
hand it to a human to check.
