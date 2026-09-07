"""Assignment 2 tests: a hidden layer of two or more solves XOR; one is not enough."""

from __future__ import annotations

from tinynn.data import XOR
from tinynn.mlp import TwoLayerNet


def test_two_hidden_solves_xor() -> None:
    """Two hidden neurons are enough to learn XOR completely."""
    net = TwoLayerNet(hidden=2, seed=1)
    net.fit(XOR)
    assert net.accuracy(XOR) == 1.0


def test_four_hidden_solves_xor() -> None:
    """More hidden neurons also solve XOR."""
    net = TwoLayerNet(hidden=4, seed=1)
    net.fit(XOR)
    assert net.accuracy(XOR) == 1.0


def test_one_hidden_is_not_enough() -> None:
    """A single hidden neuron cannot capture XOR and stays below full accuracy."""
    net = TwoLayerNet(hidden=1, seed=1)
    net.fit(XOR)
    assert net.accuracy(XOR) < 1.0
