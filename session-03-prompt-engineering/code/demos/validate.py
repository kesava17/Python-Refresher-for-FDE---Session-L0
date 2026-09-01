"""Demo 7: the output guardrail, a validator with a pass and a fail.

Before the assistant trusts any answer, it runs it through the ``Answer`` validator. A
well-formed object passes. A malformed one, here a non-escalated answer with no citation,
raises a clear error that names the problem. That error is the guardrail doing its job:
the bad answer never reaches the user.

Run:  poetry run python validate.py
"""

from __future__ import annotations

from pydantic import ValidationError

from promptlib import Answer


GOOD = {
    "answer": "Open My Orders, choose the item, and select Return. A prepaid label is emailed.",
    "citations": ["HC-003"],
    "confidence": "high",
    "escalate": False,
    "reason": "answered from return help content",
}

# Malformed: it claims to answer (escalate=False) but cites nothing to stand on.
BAD = {
    "answer": "Sure, you can definitely return that, no problem at all.",
    "citations": [],
    "confidence": "high",
    "escalate": False,
    "reason": "guessed",
}


def main() -> None:
    """Validate a good answer (passes) and a bad one (fails with a clear message)."""
    print("GOOD answer through the validator:")
    answer = Answer.model_validate(GOOD)
    print(f"    valid: {answer.model_dump()}\n")

    print("BAD answer through the validator (non-escalated but uncited):")
    try:
        Answer.model_validate(BAD)
        print("    unexpectedly valid")  # should not happen
    except ValidationError as exc:
        # pydantic reports exactly which rule failed.
        first = exc.errors()[0]
        print(f"    rejected: {first['msg']}")
        print("    the guardrail stopped it: an uncited answer never reaches the user.\n")

    print("Schema validation is the cheap, certain check every answer passes before the")
    print("assistant acts on it. Types and shape here; policy (when to escalate) next door.")


if __name__ == "__main__":
    main()
