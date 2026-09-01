"""The structured contract every later layer honours: the ``Answer`` model.

Defined once, in Session 3, as a pydantic model that is the schema and the validator in
one. Free text becomes a validated object: wrong types, a bad ``confidence`` value, or a
missing field raise here, before any caller trusts the result. Two rules that pydantic
does not get for free are added as a model validator: a ``reason`` is always present, and
a non-escalated answer must cite at least one source. The ``escalate`` field is where the
warranty and out-of-scope questions route to a human, and ``reason`` is the seed of the
compliance audit trail designed fully in Session 6.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Answer(BaseModel):
    """One support answer, in the shape the whole assistant agrees on."""

    answer: str = Field(min_length=1, description="The reply shown to the customer, or the handoff message.")
    citations: list[str] = Field(default_factory=list, description="Source doc ids the answer stands on.")
    confidence: Literal["high", "medium", "low"]
    escalate: bool = Field(description="True hands the conversation to a human agent.")
    reason: str = Field(min_length=1, description="Why this answer or escalation; the audit-trail seed.")

    @model_validator(mode="after")
    def _grounded_answers_must_cite(self) -> "Answer":
        """A non-escalated answer must cite at least one source; an escalation need not."""
        if not self.escalate and not self.citations:
            raise ValueError("a non-escalated answer must include at least one citation")
        return self


def safe_escalation(reason: str, answer: str | None = None) -> Answer:
    """Build the assistant's safe exit: a valid, escalated ``Answer``.

    Used whenever the assistant must fail closed (an injected input, unparseable model
    output, an out-of-scope topic): it always validates, and it always hands off.
    """
    return Answer(
        answer=answer or "I am handing you to a Sunrise support agent who can help with this.",
        citations=[],
        confidence="low",
        escalate=True,
        reason=reason,
    )
