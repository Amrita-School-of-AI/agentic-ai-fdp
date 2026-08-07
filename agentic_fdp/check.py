"""Setup check: `python -m agentic_fdp.check`.

Answers one question and answers it plainly: can this laptop reach the School's
model server, and does the model reply? Run before anything else on the day.
"""

from __future__ import annotations

import sys

from .config import CHAT_MODEL, EMBED_MODEL, EndpointNotFound, chat_base_url, embed_base_url

OK = "\033[32m✓\033[0m"
BAD = "\033[31m✗\033[0m"


def _check_chat() -> bool:
    try:
        url = chat_base_url()
    except EndpointNotFound as e:
        print(f"{BAD} chat server\n{e}")
        return False
    print(f"{OK} chat server        {url}")

    try:
        from .models import chat_model

        reply = chat_model().invoke("Reply with exactly: ready")
        text = (reply.content or "").strip()
        print(f"{OK} model replied      {CHAT_MODEL} -> {text!r}")
        return True
    except Exception as e:  # noqa: BLE001 — the point is to report anything at all
        print(f"{BAD} model call failed  {type(e).__name__}: {e}")
        return False


def _check_embeddings() -> bool:
    try:
        url = embed_base_url()
    except EndpointNotFound as e:
        print(f"{BAD} embedding server\n{e}")
        return False
    print(f"{OK} embedding server   {url}")

    try:
        from .models import embeddings

        vec = embeddings().embed_query("hello")
        print(f"{OK} embedding returned {EMBED_MODEL} -> {len(vec)} dimensions")
        return True
    except Exception as e:  # noqa: BLE001
        print(f"{BAD} embedding failed   {type(e).__name__}: {e}")
        return False


def main() -> int:
    print("Agentic AI FDP — setup check\n")
    chat_ok = _check_chat()
    print()
    embed_ok = _check_embeddings()

    print()
    if chat_ok and embed_ok:
        print("Everything is working. Open exercises/ex00_setup/PROBLEM.md to begin.")
        return 0

    if not chat_ok:
        print("The chat server is what blocks you. Blocks 0 to 3 and 5 need it.")
    if not embed_ok:
        print("The embedding server is only needed for block 4 (retrieval).")
    print("\nAre you on campus wifi or the Amrita VPN? That is the usual cause.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
