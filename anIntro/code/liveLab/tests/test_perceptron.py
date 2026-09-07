"""Tests for the perceptron: it learns the separable problems and fails on XOR."""

from __future__ import annotations

from tinynn.data import AND, OR, XOR
from tinynn.perceptron import Perceptron


def test_learns_or() -> None:
    """The perceptron converges on OR and classifies all four examples correctly."""
    model = Perceptron(seed=1)
    converged = model.fit(OR)
    assert converged > 0
    assert model.accuracy(OR) == 1.0


def test_learns_and() -> None:
    """The perceptron also learns AND, the other linearly separable case."""
    model = Perceptron(seed=1)
    model.fit(AND)
    assert model.accuracy(AND) == 1.0


def test_fails_on_xor() -> None:
    """The perceptron never fully learns XOR: it does not converge and stays below 100 percent."""
    model = Perceptron(seed=1)
    converged = model.fit(XOR, epochs=200)
    assert converged == -1
    assert model.accuracy(XOR) < 1.0
