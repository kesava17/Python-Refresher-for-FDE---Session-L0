"""A tiny two-layer network trained with backpropagation, enough to learn XOR.

Two inputs, one hidden layer of a few sigmoid neurons, one output. Backpropagation (the 1986
idea) sends the output error backward to adjust every weight, so the hidden layer learns too.
This is the smallest network that crosses the wall a single perceptron cannot.
"""

from __future__ import annotations

import math
import random

from tinynn.data import Example


def sigmoid(z: float) -> float:
    """A smooth activation between 0 and 1, so error can flow back through the layers."""
    return 1.0 / (1.0 + math.exp(-z))


class TwoLayerNet:
    """A 2-to-hidden-to-1 network with sigmoid activations and online backpropagation."""

    def __init__(self, hidden: int = 2, seed: int = 1) -> None:
        """Create the network with `hidden` neurons in the middle layer, weights set at random."""
        rng = random.Random(seed)
        self.hidden = hidden
        self.w1: list[list[float]] = [[rng.uniform(-1.0, 1.0) for _ in range(2)] for _ in range(hidden)]
        self.b1: list[float] = [rng.uniform(-1.0, 1.0) for _ in range(hidden)]
        self.w2: list[float] = [rng.uniform(-1.0, 1.0) for _ in range(hidden)]
        self.b2: float = rng.uniform(-1.0, 1.0)

    def forward(self, x: tuple[float, float]) -> tuple[list[float], float]:
        """Compute the hidden activations and the final output for one input."""
        hidden = [
            sigmoid(self.b1[j] + self.w1[j][0] * x[0] + self.w1[j][1] * x[1]) for j in range(self.hidden)
        ]
        output = sigmoid(self.b2 + sum(self.w2[j] * hidden[j] for j in range(self.hidden)))
        return hidden, output

    def predict(self, x: tuple[int, int]) -> int:
        """Return the network's 0/1 guess (its output rounded at 0.5)."""
        _, output = self.forward((float(x[0]), float(x[1])))
        return 1 if output >= 0.5 else 0

    def loss(self, data: list[Example]) -> float:
        """Mean squared error over the dataset: how wrong the network is on average."""
        return sum((self.forward((float(x[0]), float(x[1])))[1] - target) ** 2 for x, target in data) / len(
            data
        )

    def fit(self, data: list[Example], epochs: int = 8000, learning_rate: float = 0.5) -> None:
        """Train with online backpropagation: for each example, push the error backward and step."""
        for _ in range(epochs):
            for x, target in data:
                point = (float(x[0]), float(x[1]))
                hidden, output = self.forward(point)
                d_output = (output - target) * output * (1.0 - output)
                d_hidden = [d_output * self.w2[j] * hidden[j] * (1.0 - hidden[j]) for j in range(self.hidden)]
                for j in range(self.hidden):
                    self.w2[j] -= learning_rate * d_output * hidden[j]
                self.b2 -= learning_rate * d_output
                for j in range(self.hidden):
                    self.w1[j][0] -= learning_rate * d_hidden[j] * point[0]
                    self.w1[j][1] -= learning_rate * d_hidden[j] * point[1]
                    self.b1[j] -= learning_rate * d_hidden[j]

    def accuracy(self, data: list[Example]) -> float:
        """Fraction of the examples the network classifies correctly."""
        return sum(self.predict(x) == target for x, target in data) / len(data)
