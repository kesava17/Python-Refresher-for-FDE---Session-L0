# Live Lab: Build the Model Layer of the Sunrise Assistant

## What we're building

Session 1 gave you a GO on the **Sunrise Support Deflection Assistant**: a bot that
deflects the high-volume, low-risk questions (order status, returns, simple warranty),
routes the sensitive ones to a human, and keeps a compliant audit trail. The Prototype
phase builds that bot one layer per session. Today you build the **first layer, the model
layer**: a clean, pluggable way to call a language model, plus a harness that chooses a
model on evidence instead of hype.

By the end of this lab the `liveLab/` project has:

- A shared **help corpus** and **golden question set** that every later session reuses.
- A **Model interface** with two jobs, `generate(prompt)` and `embed(texts)`, backed by a
  deterministic offline **mock** so the whole thing runs with no API key and no network.
- A **real or on-prem adapter** that plugs in behind the same interface, selected by an
  environment variable, with its key read from the environment and never written into the
  code.
- A **model-comparison harness** that answers the golden questions with three candidate
  model configs, scores them, and prints a recommendation you can defend.
- **Tests** that pin all of it down.

You build this **through a coding agent** (Claude Code, Gemini CLI, or whichever one you
picked in the concept session). You do not hand-type the files. Your job is to give the
agent the right context, direct it one small step at a time, and **read every diff before
you accept it**. The agent does the typing; you keep the judgment.

Ground rules for the whole lab:

- Every Python command runs through `poetry run`.
- Run commands from **inside the `liveLab/` folder** unless a step says otherwise.
- It runs **fully offline by default**. No key, no network, no cost. A real model is opt-in
  and comes later.

Work in order. Copy, paste, run. After each step there is one line on what happened and why
it matters. If you have not installed Python 3.10+ and Poetry yet, do that first: see
`setup-cheatsheet.md` in this folder.

---

## Step 0: Set up and run the offline mock

First, prove the toolchain runs offline. The `demos/` project already carries a
deterministic mock model, so run it once to see a model answer with no key and no network:

```bash
cd demos
poetry install
poetry run python mock_model.py
cd ..
```

You should see deterministic answers to a few sample questions, with the warranty question
handled cautiously. That is your proof that "offline by default" is real: nothing here
reached the internet or needed a secret.

Now set up the lab project itself and confirm it installs clean:

```bash
cd liveLab
poetry install
```

**What happened.** Poetry created an isolated virtual environment for the `liveLab/`
project and installed its dependencies. You have a green, offline starting line: from here,
anything that breaks is something you (or your agent) changed, not something you inherited.
Every command from now on runs from inside `liveLab/`.

---

## Step 0b: Give your coding agent its memory

This is the coding-agent skill for this session, and you do it before you ask the agent to
build anything.

**What agent memory is, in plain terms.** A coding agent starts every task knowing nothing
about your project except what it can read in the moment. If you just say "build a model
layer," it guesses: it invents file names, picks a random library, hard-codes a fake API
key, and wanders off your conventions. **Agent memory** is a small file you keep in the
project that the agent reads first, every time. It holds the standing facts the agent must
not re-derive: your repo conventions, the contract the code must satisfy, the goal of the
layer, and the hard rules ("offline by default, no secrets"). With that file in place the
agent builds **to spec** instead of guessing, and you spend your review time on real
decisions instead of correcting the same drift over and over.

Ask your agent to create the memory file. Create `liveLab/AGENT.md` with this content (write
it yourself, or have the agent draft it and then read it line by line before saving):

```markdown
# Agent memory: Sunrise model layer (liveLab)

## Goal
Build the model layer of the Sunrise Support Deflection Assistant: a pluggable
way to call a language model, plus a harness that picks a model on evidence.
Every later session plugs into this layer.

## Repo conventions
- Python 3.10+, managed with Poetry. Run everything via `poetry run`.
- Source under `src/model_layer/`. Tests under `tests/`. Data under `data/`.
- Small, single-purpose modules. Type hints on public functions.
- Keep changes small and reviewable. One step at a time.

## The model-interface contract (do not change without asking)
- `generate(prompt: str) -> str`
- `embed(texts: list[str]) -> list[list[float]]`
- The default model is a deterministic offline `MockModel`.
- `make_model()` is a factory. It reads the env var `LLM_MODEL` (default `mock`).
  It can select a real or on-prem adapter behind the SAME interface.

## Hard rules
- Offline by default: no network call and no API key are ever required to run
  the tests or the harness.
- No secrets in code. A real adapter reads its key from the environment only.
  Never hard-code, print, or commit a key.
- Do not add conditional logic to work around a bad data shape. Fix the data.
- Do not invent libraries or endpoints. Ask if a dependency is needed.
```

**What happened.** Your agent now has a written contract it reads before each task: the
goal, the file layout, the exact `generate` / `embed` interface, and the "offline, no
secrets" rules. This is the difference between an agent that builds the layer you designed
and one that builds something plausible but wrong. You will still review every diff, but you
will be reviewing to spec.

---

## Step 1: Create the shared help corpus and golden question set

Direct the agent to build the two data files the whole phase reuses. Tell it: create
`data/help_corpus.json` (a small set of Sunrise help articles covering order status,
returns, and simple warranty) and `data/golden_questions.csv` (a handful of real support
questions, each with the expected topic and a known-good answer), plus `src/model_layer/
corpus.py` that loads both.

The corpus is a list of help articles:

```json
[
  {"id": "order-status", "title": "Where is my order?",
   "body": "Track any order from your account under Orders. Status updates within 24 hours of dispatch."},
  {"id": "returns", "title": "How do I return an item?",
   "body": "Returns are accepted within 30 days. Start a return from the order page to get a prepaid label."},
  {"id": "warranty", "title": "Warranty basics",
   "body": "Products carry a 12-month warranty. Warranty claims are reviewed before approval."}
]
```

The golden set is questions with a known answer and topic:

```csv
id,question,expected_topic,expected_answer
q1,Where is my order SE-1024?,order-status,Track it from your account under Orders.
q2,How do I return a phone?,returns,Start a return from the order page within 30 days.
q3,Is my product still under warranty?,warranty,A human confirms warranty claims before approval.
```

Confirm the loader works:

```bash
poetry run python -c "from model_layer.corpus import load_corpus, load_golden; print(len(load_corpus()), 'articles;', len(load_golden()), 'golden questions')"
```

```text
3 articles; 3 golden questions
```

**What happened.** You now have the shared ground truth for the whole program: the corpus
the bot answers from, and the golden set that decides whether an answer is good. Note the
warranty golden answer already says a human confirms it, which is the escalation guardrail
you make real in Session 3. Reuse, not rewrite, is the point: Session 4 grounds against this
same corpus and scores against this same golden set.

---

## Step 2: Build the Model interface with the deterministic mock

Now the core. Direct the agent to create `src/model_layer/model.py` with the interface, the
offline `MockModel`, and the `make_model()` factory. Point it at the contract in `AGENT.md`.

The interface is two methods, and a deterministic mock that implements them offline:

```python
class Model(Protocol):
    def generate(self, prompt: str) -> str: ...
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class MockModel:
    """Deterministic, offline. Same input always gives the same output."""

    def generate(self, prompt: str) -> str:
        # Routes to a canned answer by matched topic; warranty answers cautiously.
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        # A stable hash-based vector per text, so similar text sits closer.
        ...


def make_model(name: str | None = None) -> Model:
    name = name or os.environ.get("LLM_MODEL", "mock")
    if name == "mock":
        return MockModel()
    ...
```

`MockModel` is deterministic on purpose: the same prompt always yields the same answer, so
tests are stable and the harness is repeatable. Run it:

```bash
poetry run python -m model_layer.model "Where is my order SE-1024?"
```

```text
[mock] Track it from your account under Orders.
```

**What happened.** The rest of the PoC now has one small contract to call, `generate` and
`embed`, and never has to care which model is behind it. The offline mock means every build
in this course runs with no key and no network, so you are never blocked waiting on access.
This is the seam everything later plugs into.

---

## Step 3: Add a real or on-prem adapter behind the same interface

Direct the agent to extend `make_model()` so it can return a real or on-prem adapter, chosen
by the `LLM_MODEL` env var, with the key read from the environment. Keep the mock as the
default so the offline path never breaks.

The adapter sits behind the exact same `generate` / `embed` interface:

```python
def make_model(name: str | None = None) -> Model:
    name = name or os.environ.get("LLM_MODEL", "mock")
    if name == "mock":
        return MockModel()
    if name == "onprem":
        key = os.environ.get("LLM_API_KEY")
        if not key:
            raise RuntimeError("LLM_API_KEY is not set; onprem model needs a key from the environment")
        return OnPremModel(base_url=os.environ["LLM_BASE_URL"], api_key=key)
    raise ValueError(f"unknown LLM_MODEL: {name}")
```

The key is read from `LLM_API_KEY` at run time. It is never hard-coded, never printed, and
never committed. With no env var set, the default stays `mock`, so the offline path is
untouched:

```bash
poetry run python -m model_layer.model "How do I return a phone?"
```

```text
[mock] Start a return from the order page within 30 days.
```

Flipping to a real model later is one environment change, no code change:

```bash
# Later, on a machine that has access (not now, and never committed):
# export LLM_MODEL=onprem
# export LLM_BASE_URL=https://llm.internal.sunrise
# export LLM_API_KEY=...   # from your shell or secret store, never the repo
```

**What happened.** You can now swap in a real or on-prem model without changing a single
line of the code that calls it, because the adapter honors the same interface. The selection
is an env var and the secret comes from the environment, which is what keeps the repo clean
and keeps Sunrise's data-residency options open (an on-prem model can run inside Bharat where
the data must stay). Offline mock is still the default, so nothing you just added can break a
teammate who has no key.

---

## Step 4: Build the model-comparison harness and read its recommendation

Now the deliverable: turn "which model?" into a scored answer. Direct the agent to create
`src/model_layer/compare.py`, the harness. It answers every golden question with three
candidate model configs, scores each config on what the job needs, and prints a
recommendation with reasons.

The three candidates model the real trade-off from the deck: a big hosted model, a small
hosted model, and an in-region on-prem model. Offline, all three answer through the mock, and
each config carries the metadata the choice actually turns on:

- **Capability:** does it match the golden answers?
- **Cost:** Rs per 1,000 tokens at Sunrise volume (thousands of tickets a week).
- **Latency:** how long a customer waits.
- **Residency:** can it run where the data must stay (Bharat)?

Run the harness:

```bash
poetry run python -m model_layer.compare
```

```text
Scoring 3 configs against 3 golden questions...

config           capability   cost (Rs/1k)   latency   in-Bharat
hosted-large        3/3           0.90         slow        no
hosted-small        3/3           0.15         fast        no
onprem-mock         3/3           0.10         fast        yes

Recommendation: onprem-mock
Reason: it matches the golden set, costs the least at volume, answers fast,
and runs in region so Sunrise data stays in Bharat.
```

**What happened.** You have an instrument, not an opinion. The harness ran one task three
ways, scored each on capability, cost, latency, and residency, and produced a pick you can
defend in a design review: "this one, because it matched the golden set, costs the least at
volume, and keeps the data in Bharat." When a real adapter is available you point the harness
at it and rerun; the recommendation updates from evidence, not from a blog post. This is the
core of eval-driven selection you will reuse for grounding and for the whole PoC.

---

## Step 5: Run the tests

Lock it all down. Direct the agent to make sure `tests/` covers the interface, the factory,
the corpus loader, and the harness, then run the suite:

```bash
poetry run pytest
```

```text
tests/test_model.py ......
tests/test_corpus.py ...
tests/test_compare.py ...
============ 12 passed ============
```

The tests prove the things that must stay true: `make_model()` returns the mock by default,
`generate` and `embed` honor their signatures, the mock is deterministic (same input, same
output), the corpus and golden set load, and the harness produces a recommendation. They all
run offline, with no key, which is exactly the promise of this layer.

**What happened.** The model layer is now defended by a test suite that runs anywhere, with
no secret and no network. From here every later session extends this project, and this green
suite is the safety net that catches the agent (and you) when a change breaks the contract.

---

## You should see

Run through this recap. If each line matches, the model layer is done.

- `poetry install` in `liveLab/` completes clean, and the demo mock in `demos/` prints
  deterministic answers offline.
- `liveLab/AGENT.md` holds your agent's memory: the goal, the repo conventions, the
  `generate` / `embed` contract, and the offline-and-no-secrets rules.
- The corpus (`data/help_corpus.json`) and golden set (`data/golden_questions.csv`) load,
  and `corpus.py` reads both.
- `poetry run python -m model_layer.model "..."` returns a deterministic mock answer with no
  key set, and `make_model()` defaults to the mock.
- A real or on-prem adapter is selectable by the `LLM_MODEL` env var, with its key read from
  the environment, never from the code.
- `poetry run python -m model_layer.compare` scores three configs and prints a recommendation
  with reasons.
- `poetry run pytest` is green, entirely offline.

That is the model layer: a pluggable interface the rest of the PoC calls without caring which
model is behind it, a mock that keeps every build offline and free, an adapter seam for a real
model when you want one, and a harness that chooses on evidence. You built it through a coding
agent that you gave memory and steered one reviewed step at a time. Session 3 plugs the prompt
and structured-output layer straight into this interface.
