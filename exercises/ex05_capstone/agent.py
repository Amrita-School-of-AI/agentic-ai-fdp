"""Block 5 — Multi-Agent with goal monitoring. The capstone.

A supervisor decides what happens next; two workers do the work; an explicit
budget stops the whole thing from running forever.

Fill in the four TODOs. The graph wiring at the bottom is written for you.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from .corpus_search import search_corpus

MAX_STEPS = 8

SUPERVISOR = (
    "You direct a small team answering a question about Amrita's curriculum.\n"
    "You have two workers:\n"
    "  RESEARCH — finds facts in the curriculum documents\n"
    "  WRITE    — writes the final answer from the facts gathered so far\n\n"
    "You are shown the facts gathered and the answer written so far.\n"
    "Reply with exactly one word, checking these in order:\n"
    "  DONE     if an answer has already been written below. Do not ask for it\n"
    "           to be written again.\n"
    "  WRITE    if no answer has been written yet, and either there are enough\n"
    "           facts or research has stopped finding anything new.\n"
    "  RESEARCH only if no answer has been written and more facts would help.\n\n"
    "Two rules that matter. Never ask for RESEARCH twice running when it found\n"
    "nothing: say WRITE, so the question gets an honest 'not in the documents'\n"
    "rather than no answer at all. And once an answer exists, say DONE."
)

RESEARCHER = (
    "You are a researcher. From the passages provided, state only the facts "
    "that bear on the question, as short bullet points. If the passages do not "
    "address the question, say exactly: NOTHING RELEVANT FOUND."
)

WRITER = (
    "You are a writer. Using only the facts provided, answer the question in "
    "two or three sentences. If the facts do not answer it, say exactly: "
    "I cannot find that in the documents."
)

# The only decisions the supervisor is allowed to make. Anything else is a
# confused reply, not a new instruction.
DECISIONS = {"RESEARCH", "WRITE", "DONE"}


class State(TypedDict):
    """What flows between the agents.

    `steps` is the goal-monitoring part. Without a counter in the state there is
    nothing to stop a supervisor that keeps asking for more research, and a
    multi-agent system with no stopping condition does not fail loudly — it
    just runs, and runs, and bills you for it.
    """

    question: str
    notes: Annotated[list[str], lambda a, b: a + b]
    draft: str
    steps: int
    next: str


def _say(model: BaseChatModel, system: str, user: str) -> str:
    return model.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content


# ---------------------------------------------------------------------------
# The three nodes
# ---------------------------------------------------------------------------


def supervisor_node(state: State, model: BaseChatModel) -> dict:
    """Decide what should happen next: RESEARCH, WRITE, or DONE."""
    notes = "\n".join(state["notes"]) or "(nothing yet)"
    draft = state["draft"] or "(nothing written yet)"

    situation = (
        f"QUESTION: {state['question']}\n\n"
        f"FACTS GATHERED:\n{notes}\n\n"
        f"ANSWER SO FAR:\n{draft}"
    )

    # TODO 1
    # Ask the model, using SUPERVISOR as the system message and `situation` as
    # the human message. Normalise the reply the way you did in block 2: strip
    # whitespace and punctuation, uppercase it.
    #
    # If it is not one of RESEARCH, WRITE or DONE, fall back to WRITE — the
    # system should produce an answer rather than stall on a confused reply.
    #
    # Return {"next": decision, "steps": state["steps"] + 1}
    raise NotImplementedError("TODO 1: make the supervisor's decision")


def research_node(state: State, model: BaseChatModel) -> dict:
    """Search the corpus, then summarise what was found into a note."""
    hits = search_corpus(state["question"], k=3)

    if not hits:
        return {"notes": ["NOTHING RELEVANT FOUND."]}

    passages = "\n\n".join(f"[{source}]\n{text}" for source, text in hits)

    # TODO 2
    # Ask the model, using RESEARCHER as the system message, and give it both
    # the question and the passages. Return the reply as a new note:
    #
    #   return {"notes": [note]}
    #
    # Note the list. The state merges notes by concatenation, so each research
    # round adds to what is already there rather than replacing it.
    raise NotImplementedError("TODO 2: summarise the passages into a note")


def writer_node(state: State, model: BaseChatModel) -> dict:
    """Write the answer from the notes gathered so far."""
    # TODO 3
    # Ask the model, using WRITER as the system message, giving it the question
    # and all the notes. Return {"draft": answer}.
    raise NotImplementedError("TODO 3: write the answer from the notes")


# ---------------------------------------------------------------------------
# Routing — where goal monitoring actually happens
# ---------------------------------------------------------------------------


def route(state: State) -> str:
    """Turn the supervisor's decision into the next node to run.

    Returns "research", "write", or END.
    """
    # TODO 4
    # Two things, and the order matters.
    #
    # First the budget: if state["steps"] >= MAX_STEPS, return END no matter
    # what the supervisor said. A supervisor that keeps asking for research is
    # exactly the failure this guards against, and checking the budget second
    # would let it run one extra round every time.
    #
    # Then the decision: "RESEARCH" -> "research", "WRITE" -> "write",
    # anything else -> END.
    raise NotImplementedError("TODO 4: route on the decision, and respect the budget")


# ---------------------------------------------------------------------------
# Wiring. Written for you — read it, it is the shape of the whole system.
# ---------------------------------------------------------------------------


def build_graph(model: BaseChatModel):
    """Assemble the three nodes into a runnable graph.

        START ─▶ supervisor ─┬─▶ research ─┐
                             ├─▶ write ────┤
                             └─▶ END       │
                                  ▲        │
                                  └────────┘
                             (workers always report back)

    Both workers return to the supervisor. That is what makes it a supervised
    team rather than a fixed pipeline: after each piece of work, someone decides
    again what should happen next.
    """
    graph = StateGraph(State)

    graph.add_node("supervisor", lambda s: supervisor_node(s, model))
    graph.add_node("research", lambda s: research_node(s, model))
    graph.add_node("write", lambda s: writer_node(s, model))

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor", route, {"research": "research", "write": "write", END: END}
    )
    graph.add_edge("research", "supervisor")
    graph.add_edge("write", "supervisor")

    return graph.compile()


def run(model: BaseChatModel, question: str) -> State:
    """Answer `question` with the supervised team. Returns the final state."""
    return build_graph(model).invoke(
        {"question": question, "notes": [], "draft": "", "steps": 0, "next": ""}
    )
