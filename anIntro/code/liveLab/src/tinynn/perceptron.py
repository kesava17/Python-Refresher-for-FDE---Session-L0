"""A perceptron: one neuron that learns its own weights with Rosenblatt's 1958 rule.

It can learn any linearly separable problem (AND, OR). It cannot learn XOR, and this class is
where you see that limit for yourself.
"""

from __future__ import annotations

import random

from tinynn.data import Example
from tinynn.neuron import step, weighted_sum


class Perceptron:
    """A two-input perceptron with a learning rule."""

    def __init__(self, seed: int = 1) -> None:
        """Start from small random weights and a zero bias."""
        rng = random.Random(seed)
        self.weights: list[float] = [rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)]
        self.bias: float = 0.0

    def predict(self, x: tuple[int, int]) -> int:
        """Return the perceptron's 0/1 guess for one input pair."""
        return step(weighted_sum([float(x[0]), float(x[1])], self.weights, self.bias))

    def fit(self, data: list[Example], epochs: int = 20, learning_rate: float = 0.1) -> int:
        """Train with the perceptron rule. Return the epoch it converged, or -1 if it did not.

        On every wrong guess, nudge each weight and the bias toward the correct answer. When a
        whole pass makes no mistakes, the data is separated and training stops.
        """
        for epoch in range(1, epochs + 1):
            mistakes = 0
            for x, target in data:
                error = target - self.predict(x)
                if error != 0:
                    mistakes += 1
                    self.weights[0] += learning_rate * error * x[0]
                    self.weights[1] += learning_rate * error * x[1]
                    self.bias += learning_rate * error
            if mistakes == 0:
                return epoch
        return -1

    def accuracy(self, data: list[Example]) -> float:
        """Fraction of the examples the perceptron currently classifies correctly."""
        return sum(self.predict(x) == target for x, target in data) / len(data)
