"""Helpers for live coding in front of a room.

Model output is long, unwrapped, and unreadable on a projector, and a bare
tool-use loop prints nothing at all until it finishes. These wrap both so a
cell's output is worth showing rather than worth apologising for.

Nothing here is needed to complete the exercises. It exists for the scratchpad.
"""

from __future__ import annotations

import textwrap
import time
from typing import Any, Sequence

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# Wide enough to read from the back of a room, narrow enough not to wrap on a
# half-width projected cell.
WIDTH = 88


def show(text: Any, width: int = WIDTH) -> None:
    """Print wrapped, preserving blank lines and existing indentation."""
    for para in str(text).split("\n"):
        if not para.strip():
            print()
            continue
        indent = " " * (len(para) - len(para.lstrip()))
        print(textwrap.fill(para.strip(), width=width,
                            initial_indent=indent, subsequent_indent=indent))


def rule(title: str = "", width: int = WIDTH) -> None:
    """A labelled horizontal rule, for separating one demo from the next."""
    if title:
        print(f"\n{'─' * width}\n{title}\n{'─' * width}")
    else:
        print("─" * width)


def ask(model, question: str, system: str | None = None, *, quiet: bool = False) -> str:
    """One call, timed and wrapped. Returns the text so you can keep using it."""
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=question))

    t = time.time()
    reply = model.invoke(messages)
    elapsed = time.time() - t

    if not quiet:
        show(reply.content)
        print(f"\n[{elapsed:.1f}s]")
    return reply.content


def run_tools(model, question: str, tools: Sequence[Any], max_steps: int = 6) -> str:
    """The block 1 loop, narrating every step as it happens.

    The same logic participants write, with printing added. Use it to show a
    tool sequence live without anyone having to read a traceback of a loop.
    """
    by_name = {t.name: t for t in tools}
    bound = model.bind_tools(list(tools))
    messages = [HumanMessage(content=question)]

    print(f"Q: {question}\n")

    for step in range(1, max_steps + 1):
        reply = bound.invoke(messages)
        messages.append(reply)

        if not reply.tool_calls:
            print(f"step {step}: no tools wanted\n")
            show(reply.content)
            return reply.content

        for call in reply.tool_calls:
            try:
                result = by_name[call["name"]].invoke(call["args"])
            except KeyError:
                result = f"no such tool: {call['name']}"
            except Exception as e:  # noqa: BLE001
                result = f"{call['name']} failed: {e}"
            print(f"step {step}: {call['name']}({call['args']})")
            print(f"          -> {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    print(f"gave up after {max_steps} steps")
    return ""


def hits(chunks, width: int = WIDTH) -> None:
    """Print retrieved chunks compactly: source plus a one-line preview."""
    for i, c in enumerate(chunks, 1):
        source = c.metadata.get("source", "?")
        preview = " ".join(c.page_content.split())[: width - 24]
        print(f"{i}. [{source}]\n   {preview}...")
