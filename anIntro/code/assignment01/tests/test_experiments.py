"""Assignment 1 tests: the separable problems converge, XOR does not."""

from __future__ import annotations

from tinynn.data import AND, OR, XOR
from tinynn.perceptron import Perceptron


def test_and_and_or_converge() -> None:
    """The perceptron reaches full accuracy on AND and on OR."""
    for data in (AND, OR):
        model = Perceptron(seed=1)
        converged = model.fit(data, epochs=200)
        assert converged > 0
        assert model.accuracy(data) == 1.0


def test_xor_does_not_converge() -> None:
    """The perceptron never fully learns XOR."""
    model = Perceptron(seed=1)
    converged = model.fit(XOR, epochs=200)
    assert converged == -1
    assert model.accuracy(XOR) < 1.0
