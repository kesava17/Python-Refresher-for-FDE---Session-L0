# Assignment 2: harden the prompt against injection

Full brief and rubric: `assignment-02.md` and `solution-02.md` (in the content repo).

User input is untrusted. An attacker can hide an instruction inside an ordinary-looking
question, and because the classifier still sees a normal topic, the assistant answers
instead of refusing. This starter has **no input guardrail**: the attack slips through.

One target test fails; two must keep passing. Make them all green:

```bash
poetry install
poetry run pytest          # tests/test_injection.py: the injection test fails on the starter
```

1. **Add the input guardrail.** Fill in `INJECTION_PATTERNS` in `answerer.py` so
   `check_input` catches the attack (for example `"ignore your rules"`,
   `"reveal the system prompt"`). The guardrail runs before the model, and a hit returns
   the safe escalation.
2. **Do not over-block.** The two clean questions must still be answered. A guardrail that
   escalates everything is not a guardrail; it is an outage.

Deliverable: the input guardrail, the injection test passing, and the clean-question tests
still green.
