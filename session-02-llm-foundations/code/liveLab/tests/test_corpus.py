"""Tests for the shared help corpus and golden question set."""

from __future__ import annotations

from model_layer.corpus import load_corpus, load_golden


def test_corpus_loads_with_required_fields() -> None:
    """The corpus loads and every article carries all required fields."""
    docs = load_corpus()
    assert len(docs) >= 10
    for d in docs:
        for field in ("doc_id", "title", "source", "topic", "body"):
            assert field in d and d[field]


def test_golden_loads_with_typed_fields() -> None:
    """The golden set loads with correctly typed escalation and doc-id fields."""
    golden = load_golden()
    assert len(golden) >= 15
    for row in golden:
        assert isinstance(row["should_escalate"], bool)
        assert isinstance(row["expected_doc_ids"], list)
        assert row["question"] and row["reference_answer"]


def test_golden_has_both_answerable_and_escalation_cases() -> None:
    """The golden set contains both answerable and escalation cases."""
    golden = load_golden()
    escalate = [r for r in golden if r["should_escalate"]]
    answer = [r for r in golden if not r["should_escalate"]]
    assert escalate and answer  # the set exercises both behaviours


def test_sensitive_warranty_is_marked_for_escalation() -> None:
    """Every warranty question in the golden set is marked for escalation."""
    golden = load_golden()
    warranty = [r for r in golden if r["topic"] == "warranty"]
    assert warranty and all(r["should_escalate"] for r in warranty)
