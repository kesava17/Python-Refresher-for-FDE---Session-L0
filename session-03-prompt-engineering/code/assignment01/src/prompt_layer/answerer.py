"""Assignment 1 entry point: turn the model draft into a validated Answer."""

from __future__ import annotations

from prompt_layer.mock_llm import draft
from prompt_layer.schema import Answer


def respond(question: str) -> Answer:
    """Answer one question by validating the model draft against the Answer contract.

    On the starter this raises for a return question (the flaky prompt returns an uncited,
    non-escalated answer) and carries no ``topic``. Repair the prompt and add the field so
    both tests pass.
    """
    return Answer.model_validate(draft(question))
