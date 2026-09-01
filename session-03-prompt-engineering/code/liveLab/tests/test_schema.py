"""Tests for the Answer contract: the schema and its extra rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from prompt_layer.schema import Answer, safe_escalation


def test_valid_answer_builds() -> None:
    """A well-formed answer constructs and keeps its fields."""
    a = Answer(answer="track it in My Orders", citations=["HC-001"],
               confidence="high", escalate=False, reason="answered from HC-001")
    assert a.citations == ["HC-001"] and not a.escalate


def test_bad_confidence_is_rejected() -> None:
    """confidence outside the allowed set raises."""
    with pytest.raises(ValidationError):
        Answer(answer="x", citations=["HC-001"], confidence="sure", escalate=False, reason="ok")


def test_non_escalated_answer_must_cite() -> None:
    """A non-escalated answer with no citation is invalid."""
    with pytest.raises(ValidationError):
        Answer(answer="x", citations=[], confidence="high", escalate=False, reason="ok")


def test_escalation_needs_no_citation() -> None:
    """An escalation may carry no citation and is still valid."""
    a = Answer(answer="handoff", citations=[], confidence="low", escalate=True, reason="warranty")
    assert a.escalate


def test_empty_reason_is_rejected() -> None:
    """reason must always be set."""
    with pytest.raises(ValidationError):
        Answer(answer="x", citations=["HC-001"], confidence="high", escalate=False, reason="")


def test_safe_escalation_is_valid_and_escalates() -> None:
    """The safe exit always validates and always hands off."""
    a = safe_escalation("because the input looked unsafe")
    assert a.escalate and a.reason == "because the input looked unsafe"
