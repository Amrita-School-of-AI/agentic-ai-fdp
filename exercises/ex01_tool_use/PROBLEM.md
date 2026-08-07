# Block 1 — Tool Use

**45 minutes.** The pattern that turns a model into an agent.
Gulli, *Agentic Design Patterns*, chapter 5.

## The problem

Ask the model this:

> How many credits do 23AID304 and 24AIM332 come to together?

It cannot know. Those codes are Amrita's, the credit values live in our
curriculum, and no amount of clever prompting will retrieve a fact the model was
never shown. It will either refuse or, worse, invent a plausible number.

A model that can *call a function* has a way out. It does not need to know the
credits; it needs to know that a `course_credits` function exists and that this
question is a reason to call it.

## The loop

This is the whole pattern, and it is smaller than people expect:

```
send the messages to the model
    did the reply ask for tools?
        no  → that is the final answer, stop
        yes → run each requested tool
              append each result as a ToolMessage
              go back to the top
```

Three things make it work. The model is **told what tools exist** (`bind_tools`).
The reply may contain **`tool_calls`** instead of text. And each result goes back
as a **`ToolMessage` carrying the matching `tool_call_id`**, so the model can tell
which answer belongs to which question when it asked for several at once.

## What to build

`run_agent(model, question, tools, max_steps=6)` in `agent.py`.

Two tools are written for you in `tools.py`: `course_credits` looks up a code,
and `calculator` evaluates arithmetic. You are not writing tools today, you are
writing the loop that uses them.

Four TODOs, in order: bind the tools, write the stopping condition, dispatch each
requested tool by name, and feed the result back correctly.

## The mistake almost everyone makes

Forgetting `tool_call_id` on the `ToolMessage`, or making up a new one. The model
matches results to requests by that id. Get it wrong and the model sees an answer
to a question it did not ask.

The second most common: never stopping. If your loop always runs a tool, it never
returns. That is what `max_steps` is for, and the tests check that you respect it.

## Done when

```bash
./selfcheck ex01
uv run python -m exercises.ex01_tool_use.demo
```

Watch the demo output. You will see the model ask for `course_credits` twice, get
two numbers back, then ask for `calculator`, and only then answer. Nobody told it
that sequence. It worked it out from the question and the tool descriptions.

## Worth noticing

The tool descriptions in `tools.py` are docstrings. That is not a convenience —
the docstring is literally what the model reads when deciding whether to call it.
A vague docstring produces a vague agent. Try making one worse and re-running the
demo.
