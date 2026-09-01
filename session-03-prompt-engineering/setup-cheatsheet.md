# Setup: build the prompt layer with a coding agent

You drive **Claude Code** to build this session's layer, and you review what it produces. This
guide is not about installing a dev environment; that was settled in Session 2. It is about
**configuring the agent for the prompt and output layer** so it produces correct code you can
trust, and about where to intervene hardest when the stakes are the guardrails and the contract.

The five things to configure and the one discipline to keep are the same as Session 2. What
changes this session is the **contract** the agent must honour, the **new dependency**
(`pydantic`), and the fact that the agent is now writing **safety code**, the guardrails, which
raises the bar on your review.

---

## 0. The environment (unchanged, one reminder)

You already have Python 3.10 or later, Poetry, and Claude Code opened in the session folder.
Two reminders that matter more this session:

- **Offline by default still holds.** The layer runs on a deterministic mock plus `pydantic`.
  No API key, no network, to build or test.
- **`pydantic` is the only new dependency.** If the agent proposes any other package, stop and
  ask why. This layer needs exactly one, and it is the real tool teams use for validation.

---

## 1. Configure the agent's memory (add the contract)

Extend the Session 2 `CLAUDE.md` with the facts this layer turns on. The most important line is
the `Answer` contract: if the agent gets that wrong, everything downstream is wrong.

```markdown
# Prompt and output layer, build notes for the agent

## The Answer contract (do not change without asking)
- Fields: answer:str, citations:list[str], confidence:"high"|"medium"|"low",
  escalate:bool, reason:str.
- A non-escalated answer must cite at least one source. reason is always set.
- Warranty and out-of-scope always escalate. Low confidence escalates.

## Conventions
- Offline by default. pydantic is the only new dependency.
- Both structured-output paths (prompt-for-JSON and function-calling) end at the SAME Answer.
- The system prompt is a versioned file under prompts/, not an inline string.
- Guardrails fail closed: on any doubt, escalate rather than answer.

## Done means
- poetry run pytest is green.
- poetry run python -m prompt_layer.evaluate scores the prompt versions on the held set.
```

Keep it short and true. This memory is what keeps the agent from quietly changing a field name
or loosening a rule three files later.

---

## 2. Configure the harness (validator plus tests plus eval)

The harness this session is three things the agent (and you) can check against:

```bash
poetry run pytest                              # the tests must pass
poetry run python -m prompt_layer.evaluate     # the eval must score the prompt versions
poetry run python -c "from prompt_layer.answerer import answer; print(answer('Is my product under warranty?').escalate)"
```

Tell the agent, in the prompt and in memory, that **nothing is done until the harness is
green**: the tests pass, the evaluator runs, and a warranty question escalates. The eval is
part of the harness on purpose, because "the prompt got better" has to be a number, not a
feeling.

---

## 3. Configure your prompts (to the agent)

The same four habits as Session 2, sharpened for a layer with a contract:

- **Small, reviewable steps.** One module at a time: the schema, then the context, then Path A,
  then Path B, then the guardrails, then the eval. Not "build the prompt layer."
- **Reference the contract.** Point the agent at the `Answer` fields in `CLAUDE.md` every time,
  and tell it both paths must end at that same object.
- **State the acceptance.** End each prompt with how you will check it ("the schema rejects an
  uncited non-escalation, and pytest passes").
- **Plan before edit.** Use plan mode for anything touching the schema or the guardrails, read
  the plan, approve it, then let it edit.

A good first prompt: *"Read CLAUDE.md. In plan mode, propose how you will add the Answer pydantic
model and its validator in src/prompt_layer/schema.py, including the rule that a non-escalated
answer must cite a source. Do not edit yet."*

---

## 4. Configure skills and commands (reuse)

Package the checks you run constantly:

- **`/run-checks`** in `.claude/commands/run-checks.md`:

  ```markdown
  Run `poetry run pytest -q`, then `poetry run python -m prompt_layer.evaluate`.
  Report failures with the file and line, and stop. Do not change code unless asked.
  ```

- **A skill** for a repeatable job you will do often this session, for example
  "add a labelled question to data/prompt_tests.csv and confirm the eval still runs", so the
  held set grows the same way every time instead of by improvisation.

A `/run-checks` you trust turns the build-run-check loop into one keystroke and keeps the agent
honest between edits.

---

## 5. The loop

**prompt (with plan) -> you approve the plan -> agent edits -> `/run-checks` -> you review the
diff -> repeat until the harness is green.**

Every arrow that points back to you is deliberate. The speed comes from the agent; the
correctness comes from the loop.

---

## The discipline: man-in-the-middle, and this session it is safety code

The assistant keeps a human in the loop for the sensitive warranty cases. Building it keeps a
human in the loop too, and this session that human matters more than usual, because the agent is
writing the **guardrails**, the code whose whole job is to be correct when it counts.

**How to validate every change:**

- **Approve the plan first**, especially for the schema and the guardrails.
- **Read every diff before you accept it.** A small, reviewable diff is a feature.
- **Require the harness green.** Not "looks right"; `/run-checks` passes, and you ran it.
- **Explain it, or reject it.** If you cannot say what a guardrail change does, do not ship it.

**When to intervene hardest this session:**

- The diff **changes the `Answer` contract**: a renamed field, a relaxed type, a dropped rule.
  The whole assistant depends on this shape; a quiet change here breaks Session 4 and 5.
- The diff **weakens a guardrail to make a test pass.** An agent that loosens the citation rule,
  or flips `escalate` to dodge a check, has cheated, not fixed. The rule that caught the bug
  must still stand.
- The diff **touches the injection patterns or the escalation policy.** These are the safety
  behaviours; read them the way you would read a change to an auth check.
- The diff **adds a dependency beyond `pydantic`**, a network call, or anything that reads or
  writes a secret.
- The diff makes the **two paths disagree**, or lets an invalid `Answer` through. Both paths
  must end at the same validated object.

This is the same judgment the bot uses on a warranty case: when the stakes are real and the
confidence is not earned, a human decides. Here the stakes are the safety code you are about to
trust, and the human is you.

---

## Later: point at a real model

The offline mock and its instruction-following stand-in are the default. When you want a real or
on-prem model, plug it in at the two seams (`prompt.py` for Path A, `function_call.py` for Path
B) through the Session 2 model layer, with the key read from the environment and never committed.

```bash
export LLM_MODEL=real
export LLM_PROVIDER=your-provider
export LLM_API_KEY=your-key     # from a secret store, not the repo
```

Every caller, both paths, the guardrails, and the whole eval stay exactly the same. Only the two
seams change.
