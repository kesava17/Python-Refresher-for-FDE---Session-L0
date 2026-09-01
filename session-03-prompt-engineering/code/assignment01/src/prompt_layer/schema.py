"""The Answer contract for assignment 1 (STARTER).

This is the Session 3 contract, with one thing missing on purpose: there is no ``topic``
field yet. Part of the assignment is to add it, as a validated field against an allowed
list, so every answer is tagged with the topic it belongs to.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Answer(BaseModel):
    """One support answer. Add the ``topic`` field as part of the assignment."""

    answer: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    reason: str = Field(min_length=1)
    # TODO (assignment): add a `topic` field, validated against the allowed list
    #   order | return | warranty | out_of_scope
    # so a caller can route or report by topic. Use Literal[...] like `confidence`.

    @model_validator(mode="after")
    def _grounded_answers_must_cite(self) -> "Answer":
        """A non-escalated answer must cite at least one source; an escalation need not."""
        if not self.escalate and not self.citations:
            raise ValueError("a non-escalated answer must include at least one citation")
        return self
