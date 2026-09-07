"""Tests for the logic datasets: the truth tables are what we expect."""

from __future__ import annotations

from tinynn.data import AND, OR, XOR


def test_shapes() -> None:
    """Each dataset has four examples of two inputs and one output."""
    for dataset in (AND, OR, XOR):
        assert len(dataset) == 4
        for (a, b), target in dataset:
            assert a in (0, 1) and b in (0, 1) and target in (0, 1)


def test_xor_truth_table() -> None:
    """XOR is 1 exactly when the two inputs differ."""
    table = dict(XOR)
    assert table[(0, 0)] == 0
    assert table[(0, 1)] == 1
    assert table[(1, 0)] == 1
    assert table[(1, 1)] == 0
