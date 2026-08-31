"""A light check that the environment is set up. The real work is in my_comparison.py."""

from __future__ import annotations

from model_layer.compare import score
from model_layer.corpus import load_golden


def test_scoring_runs_offline() -> None:
    """The scoring harness runs offline and returns a well-formed result in range."""
    golden = load_golden()
    result = score("mock-large", golden)
    assert set(result) >= {"name", "score", "answered", "escalated"}
    assert 0.0 <= result["score"] <= 100.0
