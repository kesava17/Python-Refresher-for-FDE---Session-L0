"""A single neuron: a weighted sum of inputs plus a bias, through a step activation."""

from __future__ import annotations


def step(total: float) -> int:
    """The activation: fire (1) if the total is at least zero, otherwise 0."""
    return 1 if total >= 0.0 else 0


def weighted_sum(inputs: list[float], weights: list[float], bias: float) -> float:
    """Combine inputs and weights into one number: bias plus the sum of weight times input."""
    return bias + sum(w * x for w, x in zip(weights, inputs, strict=True))
