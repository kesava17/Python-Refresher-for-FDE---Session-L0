"""Guardrails: an input guard before the model, an output policy after it.

Two checks the model does not get to skip. The input guard treats the question as
untrusted and catches prompt-injection attempts before the model runs. The output policy
enforces the escalation rules the business case demands regardless of what the model
returned: warranty and out-of-scope always go to a human, and a low-confidence answer is
never shown as if it were sure. Both fail closed: when in doubt, escalate.
"""

from __future__ import annotations

from prompt_layer.mock_llm import classify
from prompt_layer.schema import Answer, safe_escalation

_INJECTION_PATTERNS = [
    "ignore your rules",
    "ignore previous",
    "ignore all instructions",
    "disregard",
    "forget your instructions",
    "reveal the system prompt",
    "show me your system prompt",
    "what is your system prompt",
    "you are now",
]


def check_input(question: str) -> str | None:
    """Return a reason string if the input looks like an injection attempt, else None."""
    low = question.lower()
    for pattern in _INJECTION_PATTERNS:
        if pattern in low:
            return f"input guardrail: possible prompt-injection attempt ({pattern!r})"
    return None


def apply_output_policy(answer: Answer, question: str) -> Answer:
    """Force an escalation when policy requires it, whatever the model returned.

    Warranty and out-of-scope topics always route to a human, and a low-confidence answer
    escalates rather than being shown as certain. If the answer already escalates, or is a
    confident in-scope answer, it passes through unchanged.
    """
    topic = classify(question)

    if not answer.escalate and topic in ("warranty", "out_of_scope"):
        return safe_escalation(
            f"output policy: {topic} topic must be handled by a human",
            answer="This needs a Sunrise support agent. I am handing you over now.",
        )
    if not answer.escalate and answer.confidence == "low":
        return safe_escalation(
            "output policy: confidence too low to answer without a human",
            answer="I am not confident enough to answer this. Let me bring in a support agent.",
        )
    return answer
