"""Finding the School's model server, without anyone in the room guessing.

The chat server is reachable at different addresses depending on where you are
sitting. On campus wifi it answers on its campus VLAN address; over the staff
VPN only the cluster-private address routes. Rather than print three URLs on a
slide and hope, we probe all of them once, cache the winner, and move on.

Environment overrides always win, so a participant on a different network, or
another institution running this workshop against their own server, changes one
variable and nothing else:

    FDP_CHAT_URL    full base URL including /v1
    FDP_EMBED_URL   full base URL including /v1
    FDP_MODEL       chat model name
    FDP_EMBED_MODEL embedding model name
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from pathlib import Path

# Probed in order; the first that answers wins.
CANDIDATE_HOSTS = ["10.13.20.12", "10.13.16.12", "172.17.16.12"]

CHAT_PORT = 8001
EMBED_PORT = 8002

CHAT_MODEL = os.environ.get("FDP_MODEL", "google/gemma-4-26B-A4B-it")
EMBED_MODEL = os.environ.get("FDP_EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# The server requires no key. The OpenAI client refuses to start without one,
# so we send a placeholder.
API_KEY = os.environ.get("FDP_API_KEY", "not-needed")

_CACHE = Path.home() / ".cache" / "agentic-fdp" / "endpoints.json"
_PROBE_TIMEOUT = 2.0


class EndpointNotFound(RuntimeError):
    """Raised when no candidate address answers, with what to try next."""


def _reachable(host: str, port: int, path: str) -> bool:
    url = f"http://{host}:{port}{path}"
    try:
        with urllib.request.urlopen(url, timeout=_PROBE_TIMEOUT) as r:
            return r.status == 200
    except (urllib.error.URLError, socket.timeout, OSError):
        return False


def _load_cache() -> dict:
    try:
        return json.loads(_CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(data: dict) -> None:
    try:
        _CACHE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE.write_text(json.dumps(data, indent=2))
    except OSError:
        # A read-only home is not a reason to fail; we just probe again later.
        pass


def _discover(kind: str, port: int, health_path: str, env_var: str) -> str:
    override = os.environ.get(env_var)
    if override:
        return override.rstrip("/")

    cache = _load_cache()
    cached = cache.get(kind)
    if cached and _reachable(cached["host"], port, health_path):
        return f"http://{cached['host']}:{port}/v1"

    for host in CANDIDATE_HOSTS:
        if _reachable(host, port, health_path):
            cache[kind] = {"host": host}
            _save_cache(cache)
            return f"http://{host}:{port}/v1"

    raise EndpointNotFound(
        f"No {kind} server answered on port {port}.\n"
        f"  Tried: {', '.join(CANDIDATE_HOSTS)}\n"
        f"  If you are off campus, connect to the Amrita VPN.\n"
        f"  If your instructor gave you a different address, set {env_var}, "
        f"for example:\n"
        f"    export {env_var}=http://<host>:{port}/v1"
    )


def chat_base_url() -> str:
    """Base URL of the chat server, discovered or overridden."""
    return _discover("chat", CHAT_PORT, "/v1/models", "FDP_CHAT_URL")


def embed_base_url() -> str:
    """Base URL of the embeddings server, discovered or overridden."""
    return _discover("embed", EMBED_PORT, "/health", "FDP_EMBED_URL")


def describe() -> str:
    """One-line summary for the setup check, or the reason it cannot connect."""
    lines = []
    for label, fn, model in (
        ("chat", chat_base_url, CHAT_MODEL),
        ("embeddings", embed_base_url, EMBED_MODEL),
    ):
        try:
            lines.append(f"  {label:<11} {fn()}  ({model})")
        except EndpointNotFound as e:
            lines.append(f"  {label:<11} NOT REACHABLE\n{e}")
    return "\n".join(lines)
