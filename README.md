# Agentic AI, Hands On

[![selfcheck](https://github.com/Amrita-School-of-AI/agentic-ai-fdp/actions/workflows/selfcheck.yml/badge.svg)](https://github.com/Amrita-School-of-AI/agentic-ai-fdp/actions/workflows/selfcheck.yml)

**Amrita School of AI, Coimbatore** · Faculty Development Programme
Dr. Abhijith Anandakrishnan, Assistant Professor

> The badge above is **red on this repository, and that is correct**. The
> exercises here are unsolved starters, so the tests fail by design. It turns
> green on your fork as you complete the blocks.

A one-day workshop in which you build six working AI agents, starting from a
single model call and finishing with a supervised multi-agent system. Everything
runs against the School's own model server. Nothing here needs an account with
an AI company, and no exercise costs money to run.

---

## Before you start

Works on **Linux, macOS and Windows**. You need `git` and about ten minutes.
You do *not* need to install Python first — `uv` does that for you.

Windows users: use **PowerShell**, not the old Command Prompt. Press Start, type
`powershell`, press Enter. Your prompt should begin `PS C:\...`.

**1. Install `uv`** (a fast Python package manager; skip if you have it):

<table>
<tr><td><b>Linux / macOS</b></td><td>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</td></tr>
<tr><td><b>Windows</b></td><td>

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

</td></tr>
</table>

**Then close your terminal and open a new one**, so it picks up the changed
`PATH`. Skipping this is the most common cause of `uv: command not found`
straight after a successful install. Check with `uv --version`.

**2. Fork this repository** on GitHub (the **Fork** button, top right). You want
your own copy, because you will be pushing to it.

**3. Clone your fork and build the environment.** Same on all platforms:

```
git clone https://github.com/<your-username>/agentic-ai-fdp.git
cd agentic-ai-fdp
uv sync
```

**4. Check that everything works:**

```
uv run python -m agentic_fdp.check
```

You should see the address of the chat server, the address of the embedding
server, and a one-line reply from the model. If you do not, the
[troubleshooting section](#when-something-does-not-work) has the fix.

You must be on **campus wifi** or the **Amrita VPN**. The model server is on the
School's own network and is not exposed to the public internet.

> **Windows note.** If your Documents folder syncs to OneDrive, clone somewhere
> else — `C:\Users\<you>\agentic-ai-fdp` is fine. OneDrive syncing a virtual
> environment while `uv` is writing to it causes file-lock errors that look like
> a corrupted install.

---

## The day

| | Block | Pattern | Time |
|---|---|---|---|
| 0 | `ex00_setup` | Your first model call | 15 min |
| 1 | `ex01_tool_use` | **Tool Use** | 45 min |
| 2 | `ex02_chaining_routing` | **Prompt Chaining** and **Routing** | 45 min |
| 3 | `ex03_reflection` | **Reflection** | 45 min |
| 4 | `ex04_rag` | **Knowledge Retrieval** | 60 min |
| 5 | `ex05_capstone` | **Multi-Agent** with goal monitoring | 75 min |

Each block sits in its own folder under `exercises/` and contains:

- `PROBLEM.md` — what to build, and why the pattern exists
- `agent.py` — the file you edit, with the parts you write marked `TODO`
- `test_*.py` — the tests that decide whether you got it right
- `demo.py` — the same code run against the real model, for you to play with

---

## How to work through an exercise

Open the folder, read `PROBLEM.md`, then edit `agent.py`. Fill in each `TODO`.
The scaffolding around them is already written; you are wiring up the pattern,
not fighting Python.

Check your work at any time:

<table>
<tr><td><b>Linux / macOS</b></td><td>

```bash
./selfcheck ex01      # just this block
./selfcheck           # every block
```

</td></tr>
<tr><td><b>Windows</b></td><td>

```powershell
uv run python selfcheck ex01
uv run python selfcheck
```

</td></tr>
</table>

On Windows, `./selfcheck` alone does not work: PowerShell has no concept of the
`#!` line that tells Linux and macOS which interpreter to use. Put
`uv run python` in front and it behaves identically.

Green means the pattern is wired correctly. Red prints the failing test and a
plain-English hint.

Then watch it run for real. This one is the same on every platform:

```
uv run python -m exercises.ex01_tool_use.demo
```

Note the dots and the missing `.py`: that names a Python module rather than a
file path, which is why it works identically everywhere.

### Commit and push to check it in the cloud too

```bash
git add -A
git commit -m "ex01 done"
git push
```

GitHub runs the same tests and shows a block-by-block table under the **Actions**
tab, like this:

| Block | Pattern | Result |
|---|---|---|
| `ex00_setup` | Your first model call | ✅ passed |
| `ex01_tool_use` | Tool Use | ✅ passed |
| `ex02_chaining_routing` | Prompt Chaining and Routing | ❌ the second call did not receive the first call's output |

When every block passes, the badge on your fork turns green.

> Push to **your own fork**, not to this repository. Fork it from the GitHub web
> interface first, then clone your fork instead of this one.

---

## Why the tests do not call the real model

A language model can answer the same question two different ways. If the tests
called the real server, a correct solution would sometimes fail and a wrong one
would sometimes pass, and you would have no way to tell which had happened.

So the tests run against a scripted stand-in that returns fixed replies. A test
failure therefore means one thing only: the pattern is wired up wrongly. It also
means the tests still pass on a laptop with no network, long after the workshop.

The real model is still the point of the day. That is what `demo.py` is for: the
tests check the wiring, the demo shows the behaviour.

---

## When something does not work

| What you see | What to do |
|---|---|
| `No chat server answered on port 8001` | You are not on campus wifi or the Amrita VPN. Connect, then try again. |
| Still unreachable after connecting | Your instructor will give you an address. Linux/macOS: `export FDP_CHAT_URL=http://<host>:8001/v1` · Windows: `$env:FDP_CHAT_URL="http://<host>:8001/v1"` |
| `command not found: uv` | Close the terminal and open a new one, so your shell picks up the new `PATH`. |
| `./selfcheck` does nothing useful on Windows | Use `uv run python selfcheck` instead. PowerShell cannot run it directly. |
| `running scripts is disabled on this system` (Windows) | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then retry. This lasts for that window only. |
| `uv sync` is very slow | Thirty laptops are downloading at once. It finishes; give it a few minutes. On Windows, corporate antivirus also scans each file as it is written. |
| A test fails and the message mentions the script | Your loop is not stopping. Read the hint in the failure, it names the condition. |
| Everything fails after you edited something | `git diff` to see what changed, or `git checkout exercises/` to start that block again. |

If none of that helps, raise your hand. That is what the day is for.

---

## Running this workshop yourself

The material is deliberately portable. To run it at another institution, point
it at your own OpenAI-compatible server:

**Linux / macOS**

```bash
export FDP_CHAT_URL=http://your-server:8000/v1
export FDP_MODEL=your-model-name
export FDP_EMBED_URL=http://your-server:8002/v1
export FDP_EMBED_MODEL=your-embedding-model
```

**Windows (PowerShell)**

```powershell
$env:FDP_CHAT_URL   = "http://your-server:8000/v1"
$env:FDP_MODEL      = "your-model-name"
$env:FDP_EMBED_URL  = "http://your-server:8002/v1"
$env:FDP_EMBED_MODEL= "your-embedding-model"
```

Either way these last only for the current terminal. To make them permanent,
add the `export` lines to `~/.bashrc` or `~/.zshrc`, or on Windows use
`setx FDP_CHAT_URL "http://your-server:8000/v1"` and open a new terminal.

Nothing else changes. The exercises, tests and CI all read these variables.
`docs/` holds the slides, the guide and the instructor handbook, which includes
the timing plan and the notes for running each block.

---

## Source and further reading

The patterns taught here are the well-established ones in the field. For a
book-length treatment, see **Antonio Gulli, _Agentic Design Patterns: A Hands-On
Guide to Building Intelligent Systems_**, which each block cites by chapter. The
material in this repository is written independently; the chapter references are
there so you can read further, not because the text is drawn from it.

---

## Licence

Teaching material, free to reuse and adapt with attribution.
The corpus under `corpus/` is assembled from curriculum documents published on
Amrita Vishwa Vidyapeetham's own public web host; see `corpus/README.md` for the
source URLs.
