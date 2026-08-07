"""Block 2 — Prompt Chaining and Routing.

Two small patterns that compose into most real systems.
Fill in the four TODOs.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

# ---------------------------------------------------------------------------
# Part A — Prompt Chaining
# ---------------------------------------------------------------------------

EXTRACT = (
    "Extract the key facts from the text as short bullet points. "
    "Facts only, no commentary."
)

HEADLINE = (
    "Write a single headline of at most twelve words summarising these facts. "
    "Reply with the headline only, no quotation marks."
)


def chain(model: BaseChatModel, text: str) -> tuple[str, str]:
    """Two calls, where the second reads the first's output.

    Extract facts, then headline those facts. Returns (facts, headline).

    Why not one call? Because "extract then summarise" asks the model to do two
    different jobs at once, and it does both worse. Splitting the work means
    each call has one instruction, and you get to see and check the middle step.
    """
    # TODO 1
    # First call: apply EXTRACT to `text`. Keep the reply text in `facts`.
    facts = None  # replace this

    # TODO 2
    # Second call: apply HEADLINE to `facts` — not to `text`. That is the whole
    # point of a chain: the second stage consumes the first stage's output.
    headline = None  # replace this

    return facts, headline


# ---------------------------------------------------------------------------
# Part B — Routing
# ---------------------------------------------------------------------------

# Each route is a name and the system message that handles it. Note that the
# handlers differ *only* by system message: one model, three personalities.
ROUTES = {
    "maths": "You are a maths tutor. Solve the problem and show one line of working.",
    "policy": (
        "You are an academic office clerk. Answer questions about rules, credits "
        "and regulations plainly. If you do not know, say so."
    ),
    "other": "You are a helpful assistant. Answer briefly.",
}

ROUTER = (
    "Classify the question into exactly one category.\n"
    "Reply with one word only, no punctuation, no explanation.\n\n"
    "maths  — arithmetic, algebra, calculation, anything with numbers to work out\n"
    "policy — course credits, regulations, attendance, examination rules\n"
    "other  — anything else\n"
)


def pick_route(model: BaseChatModel, question: str) -> str:
    """Ask the model which handler should take this question.

    Must return one of the keys of ROUTES. A model asked for one word will
    sometimes still produce "Maths." or "the category is maths" — so normalise
    the reply, and fall back to "other" if it is not recognised. A router that
    crashes on an unexpected word is a router that crashes in front of a class.
    """
    # TODO 3
    # Call the model with ROUTER as the system message and `question` as the
    # human message. Then normalise: strip whitespace and punctuation, lowercase.
    # If the result is not a key of ROUTES, return "other".
    raise NotImplementedError("TODO 3: classify the question into one of ROUTES")


def route_and_answer(model: BaseChatModel, question: str) -> tuple[str, str]:
    """Pick a route, then answer with that route's system message.

    Returns (route_name, answer).
    """
    route = pick_route(model, question)

    # TODO 4
    # Answer the question using ROUTES[route] as the system message.
    # Return (route, answer).
    raise NotImplementedError("TODO 4: answer using the chosen route's system message")
