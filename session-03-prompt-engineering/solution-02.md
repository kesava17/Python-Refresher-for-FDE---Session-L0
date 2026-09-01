# Solution 02 · Harden the prompt against injection

> The worked solution for Assignment 02. Try the assignment yourself first. This is here to
> check your work, or to unstick you. There is a correct method: check untrusted input before
> the model runs, key the check on override language, keep honest questions flowing, and be
> honest about what the control misses. This solution shows the fix and the reasoning.

The assignment is not about a list of banned phrases; it is about a stance. Everything the
user types, and everything a document says, is data, not instructions. A guardrail encodes
that stance as a check that runs before the model, and it is judged on both sides at once:
what it stops and what it lets through. Below is the reference fix and the rubric.

## What a strong guardrail shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Runs before the model** | The check happens on the raw input, ahead of generation, so the injected instruction never reaches the model. A check applied to the output only is too late. |
| **Keys on the attack, not the topic** | Patterns match override language (`"ignore your rules"`, `"reveal the system prompt"`), not the innocent topic the attack is wrapped in. |
| **Fails closed** | A hit returns the safe escalation (a valid, escalated `Answer`), not a crash and not a partial answer. |
| **Does not over-block** | Both clean questions still answer. Patterns are specific phrases, not common single words that appear in honest questions. |
| **Maintained, not one-shot** | An evasion variant was added to the test and then defended against. The defence is treated as a living held set of attacks. |
| **Honest about limits** | The residual risk is named, and the output policy is identified as the backstop. |

The trap is the over-broad guardrail. It is easy to pass the injection test by escalating
anything that smells suspicious, and easy to miss that you have started escalating "How do I
ignore a return label?" along with it. Safety that blocks real customers is not safety; the
mark requires both tests on the clean side to stay green.

## The reference fix

Fill in the pattern list in `answerer.py`. The stub `check_input` and `respond` already do the
rest.

```python
INJECTION_PATTERNS = [
    "ignore your rules",
    "ignore previous instructions",
    "disregard your instructions",
    "forget the rules",
    "reveal the system prompt",
    "show me your system prompt",
]
```

Run the tests:

```bash
poetry run pytest
# 3 passed
```

`check_input` lower-cases the question and returns a reason on the first pattern it finds;
`respond` turns that reason into `safe_escalation(...)`, a valid `Answer` with `escalate=True`.
The attack is refused; the two clean questions, which contain none of the patterns, flow
through to the model as before.

## Why this is the right shape

A classifier tells you what a question is about; it cannot tell you whether the question is
trying to manipulate you. Those are different jobs, so they are different checks. Putting the
guardrail before the model, on the raw text, is what makes it a guardrail and not a
post-hoc filter: the malicious instruction is stopped before it can influence a single token.

Keying on override language rather than the topic is what keeps the false-positive rate down.
The words that make the attack an attack are `ignore`, `disregard`, `reveal the system prompt`,
not `return` or `order`. Specific phrases catch the attempt while leaving honest questions,
which never contain that language, untouched.

And naming the limits is part of the engineering, not an apology for it. Pattern-matching
catches the common phrasings and buys you a great deal for a little code, but a determined
attacker will reword, translate, or hide the instruction in a retrieved document. That is why
the output policy still escalates sensitive topics and low-confidence answers: a missed
injection has a second gate to clear. Defence in depth means no single control has to be
perfect.

## Going further (optional)

- Move the pattern list to a small data file and load it, so adding a newly seen attack is a
  data change, not a code change, and the list can be reviewed on its own.
- Add a check on retrieved passages, not just the user's question, so an instruction planted
  in a document is caught the same way. This is the indirect-injection case, and it is the one
  that surprises teams most.
- Log every blocked attempt with its reason. That log is both an audit record and the raw
  material for the next round of patterns.
