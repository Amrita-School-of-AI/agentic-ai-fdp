# Block 0 — Your first model call

**15 minutes.** No pattern yet. We are checking that your laptop can talk to the
School's model server, and putting the two ideas everything else rests on in
front of you.

## The two ideas

**A chat model takes a list of messages and returns one message.** That is the
whole interface. Not a string in and a string out: a *list of messages* in, and
one message out. Everything in this workshop is a way of deciding what goes into
that list.

**Messages have roles.** A `SystemMessage` says who the model is being right
now. A `HumanMessage` is what the user said. An `AIMessage` is what the model
said. Later we add a fourth, `ToolMessage`, which is what a tool returned, and
that fourth one is where agents begin.

## What to build

Open `agent.py`. Two functions, both small.

`ask(model, question)` sends one question and returns the model's reply as plain
text. `ask_as(model, role, question)` does the same but first tells the model
who to be, which is how you get a maths tutor and a policy clerk out of one
model.

## Why we bother with the system message

Try `demo.py` both ways once the tests pass. The same question, answered by
"you are a strict examiner" and by "you are an encouraging tutor", comes back
different. That difference is not decoration. In block 2 you will route a
question to one of several handlers, and the only thing distinguishing those
handlers is their system message.

## Done when

```bash
./selfcheck ex00
```

is green, and

```bash
uv run python exercises/ex00_setup/demo.py
```

prints a real answer from the server.

## Read further

The distinction between a model and an agent is the subject of the opening
chapter of Gulli's *Agentic Design Patterns*. We build the first actual agent in
block 1.
