"""The Answer contract for assignment 2, plus the safe exit."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Answer(BaseModel):
    """One support answer, in the shape the whole assistant agrees on."""

    answer: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def _grounded_answers_must_cite(self) -> "Answer":
        """A non-escalated answer must cite at least one source; an escalation need not."""
        if not self.escalate and not self.citations:
            raise ValueError("a non-escalated answer must include at least one citation")
        return self


def safe_escalation(reason: str) -> Answer:
    """The assistant's safe exit: a valid, escalated Answer that hands off to a human."""
    return Answer(
        answer="I am handing you to a Sunrise support agent who can help with this.",
        citations=[],
        confidence="low",
        escalate=True,
        reason=reason,
    )
