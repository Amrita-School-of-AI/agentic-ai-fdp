"""Block 3 — Reflection.

The model checks its own work and revises it. Fill in the three TODOs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

DRAFT = "You are a technical writer. Write the requested text. Be concrete and brief."

CRITIC = (
    "You are a strict reviewer. Judge the text against the brief.\n"
    "If it fully meets the brief, reply with exactly: APPROVED\n"
    "Otherwise list what is wrong, as short bullet points. Do not rewrite it."
)

REVISE = (
    "You are a technical writer. Rewrite the text so it addresses every point "
    "of the critique. Reply with the revised text only."
)

APPROVAL = "APPROVED"


@dataclass
class Reflection:
    """The result, plus the trail of how it got there.

    Keeping the intermediate drafts is not decoration. Reflection is expensive —
    three model calls where one might do — and the only way to judge whether it
    earned its cost is to read what changed between rounds.
    """

    final: str
    rounds: int
    drafts: list[str] = field(default_factory=list)
    critiques: list[str] = field(default_factory=list)
    approved: bool = False


def _say(model: BaseChatModel, system: str, user: str) -> str:
    """One call with a system message. Provided, so you write the loop, not this."""
    return model.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content


def reflect(model: BaseChatModel, brief: str, max_rounds: int = 3) -> Reflection:
    """Draft, critique, revise — until the critic approves or the rounds run out.

        draft ──▶ critique ──▶ approved?  ──yes──▶ done
                      ▲            │
                      └── revise ◀─┘ no

    `max_rounds` counts critique rounds. A critic that never approves must not
    loop forever, and returning the best draft so far beats raising.
    """
    draft = _say(model, DRAFT, brief)
    result = Reflection(final=draft, rounds=0, drafts=[draft])

    for _ in range(max_rounds):
        # TODO 1
        # Ask the critic to judge the current draft against the brief.
        # Give it both: it cannot judge a text without knowing what was asked.
        # Use _say(model, CRITIC, ...) and record it in result.critiques.
        critique = None  # replace this

        # TODO 2
        # Decide whether the critic approved. It was told to reply with exactly
        # APPROVED, but models add full stops and pleasantries, so test for the
        # word appearing in the reply rather than the reply being equal to it.
        #
        # On approval: mark result.approved, set result.final, and return.

        # TODO 3
        # Not approved: revise. Give the reviser the brief, the current draft
        # and the critique, then make the revision the new current draft and
        # record it in result.drafts. Remember to update result.final too, so a
        # run that never gets approved still returns its most improved version.
        result.rounds += 1

    return result
