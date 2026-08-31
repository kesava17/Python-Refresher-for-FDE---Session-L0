# Setup: build this live lab with a coding agent

From this session on, you do not hand-write the lab. You **drive a coding agent** to
build it, and you review what it produces. This guide is not about installing a dev
environment; it is about **configuring the agent and the build loop** so the agent
produces correct code you can trust. We use **Claude Code**.

There are five things to configure, and one discipline to keep:

1. the **environment** the agent works in,
2. the agent's **memory**,
3. the **harness** that checks the agent's work,
4. the **prompts** you give it,
5. reusable **skills and commands**,

and the discipline: **man-in-the-middle**, you validate every change the agent makes.

---

## 0. The environment (once)

The agent needs a clean, offline, secret-free place to work.

- **Offline by default.** The lab runs with the deterministic mock model, no API key.
  The agent never needs a network or a key to build or test.
- **Secrets stay in the environment, never in the repo.** If you later plug in a real
  model, its key comes from an environment variable (`LLM_API_KEY`), read at run time.
  Tell the agent this in its memory (next step), so it never writes a key into a file.
- **Prerequisites** are minimal and you set them up once: Python 3.10 or later, Poetry,
  and Claude Code, opened in the session folder. That is the last time this guide talks
  about a dev environment. Everything below is about the agent.

---

## 1. Configure the agent's memory

A coding agent with no memory guesses. Give it a project memory so it builds to spec.
In Claude Code this is a **`CLAUDE.md`** file at the project root; the agent reads it on
every turn.

Create `CLAUDE.md` with the facts the agent must not get wrong:

```markdown
# Model layer, build notes for the agent

## Goal
Build the model layer of the Sunrise Support Deflection Assistant: one small interface
with a pluggable model behind it, and a harness that picks a model on evidence.

## Conventions
- Offline by default: the deterministic mock is the default model. No network, no key.
- Secrets come from environment variables only. Never write a key into a file.
- Program to the interface. Callers use generate() and embed(); they never import a
  concrete model.

## The contract (do not change without asking)
- Model.generate(prompt: str) -> str
- Model.embed(texts: list[str]) -> list[list[float]]
- make_model() returns the offline mock unless LLM_MODEL selects another.

## Done means
- poetry run pytest is green.
- poetry run python -m model_layer.compare prints a scored recommendation.
```

That memory is the difference between an agent that builds your model layer and one that
builds a generic chatbot. Keep it short and true; update it when the design moves.

---

## 2. Configure the harness (the agent's feedback loop)

The agent needs a way to know it is right, and so do you. The **harness** is the tests
plus the comparison run. It is the agent's ground truth.

```bash
poetry run pytest                          # the tests must pass
poetry run python -m model_layer.compare   # the harness must print a recommendation
```

Tell the agent, in the prompt and in memory, that **nothing is done until the harness is
green**. The agent's job is then a loop: change the code, run the harness, read the
failures, fix, repeat. You are not asking it to "write some code"; you are asking it to
**make the harness pass**, which is a target it can check itself.

---

## 3. Configure your prompts

How you ask decides what you get. Four habits:

- **Small, reviewable steps.** One layer at a time (the interface, then the mock, then
  the adapter, then the harness, then the tests), not "build the whole thing."
- **Reference the files and the contract.** Point the agent at `CLAUDE.md` and the exact
  interface it must honour.
- **State the acceptance.** End each prompt with how you will check it ("the new tests
  pass, and compare still runs").
- **Plan before edit.** Use Claude Code's **plan mode**: ask the agent to propose a plan,
  read it, approve it, and only then let it edit. This is your first checkpoint.

A good first prompt looks like: *"Read CLAUDE.md. In plan mode, propose how you will add
the Model interface and the deterministic MockModel in src/model_layer/model.py. Do not
edit yet."*

---

## 4. Configure skills and commands (reuse)

You will run the same checks and the same small jobs many times. Package them so you do
not retype them.

- **Custom slash commands** live in `.claude/commands/`. A file `run-checks.md` with the
  body below becomes the command `/run-checks`:

  ```markdown
  Run `poetry run pytest -q` and `poetry run python -m model_layer.compare`.
  Report failures with the file and line, and stop. Do not change code unless asked.
  ```

- **Skills** package a repeatable workflow with its own instructions (for example
  "add a help-center doc to the corpus and a golden question for it"), so the agent
  follows the same steps every time instead of improvising.

Reuse is the point: a `/run-checks` you trust turns the build-run-check loop into one
keystroke, and keeps the agent honest between edits.

---

## 5. The loop

Put it together and the build is a loop, not a monologue:

**prompt (with plan) -> you approve the plan -> agent edits -> `/run-checks` -> you review
the diff -> repeat until the harness is green.**

Every arrow that points back to you is deliberate. The speed comes from the agent; the
correctness comes from the loop.

---

## The discipline: man-in-the-middle on the agent's code

The assistant you are building keeps a human in the loop for the sensitive warranty
cases. Building it keeps a human in the loop too, and that human is **you, validating the
code the agent generates.** An agent is fast and confident, and sometimes confidently
wrong. You are the check.

**How to validate every change:**

- **Approve the plan first.** In plan mode, read the plan before any file changes. If the
  plan is wrong, the code will be too.
- **Read every diff before you accept it.** Do not accept edits you have not read. A
  small, reviewable diff is a feature, not a slowdown.
- **Require the harness green.** A change is not done because it "looks right"; it is done
  when `/run-checks` passes. Run it yourself.
- **Explain it, or reject it.** If you cannot explain what a change does, do not ship it.
  Ask the agent to simplify or to walk you through it.

**When to intervene hardest:**

- The diff is large, or touches many files at once.
- It adds a dependency, a network call, or anything that reads or writes a secret.
- It changes the interface contract, the offline-by-default rule, or the tests
  themselves (an agent that edits the test to make it pass has cheated, not fixed).
- It invents a file, an API, or a function that does not exist.

This is the same judgment the bot uses on a warranty case: when the stakes are real and
the confidence is not earned, a human decides. Here the stakes are the code you are about
to trust, and the human is you.

---

## Later: point at a real model

When you want a real or on-prem model, set the environment and never commit the key. The
offline mock stays the default, so the build and the tests keep running for everyone.

```bash
export LLM_MODEL=real
export LLM_PROVIDER=your-provider
export LLM_API_KEY=your-key     # from a secret store, not the repo
```

The `RealModel` adapter is the only seam that changes. Every caller, and the whole
harness, stays exactly the same.
