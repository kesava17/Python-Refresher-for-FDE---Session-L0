"""Crossing the wall: a two-layer network learns XOR with backpropagation.

Add one hidden layer of two neurons and train it with backpropagation (the 1986 idea), and
the network that a single perceptron could never manage learns XOR cleanly. This is the whole
jump from a single layer to a deep network, in about forty lines. Standard library only.

Run:  poetry run python demo_xor_mlp.py
"""

from __future__ import annotations

import math
import random

Example = tuple[tuple[float, float], float]
XOR_DATA: list[Example] = [((0.0, 0.0), 0.0), ((0.0, 1.0), 1.0), ((1.0, 0.0), 1.0), ((1.0, 1.0), 0.0)]


def sigmoid(z: float) -> float:
    """A smooth activation between 0 and 1, so error can flow back through the layers."""
    return 1.0 / (1.0 + math.exp(-z))


class TwoLayerNet:
    """A tiny 2-2-1 network: two inputs, one hidden layer of two neurons, one output."""

    def __init__(self, seed: int = 1) -> None:
        """Initialize the weights and biases at random."""
        rng = random.Random(seed)
        self.w1: list[list[float]] = [[rng.uniform(-1.0, 1.0) for _ in range(2)] for _ in range(2)]
        self.b1: list[float] = [rng.uniform(-1.0, 1.0) for _ in range(2)]
        self.w2: list[float] = [rng.uniform(-1.0, 1.0) for _ in range(2)]
        self.b2: float = rng.uniform(-1.0, 1.0)

    def forward(self, x: tuple[float, float]) -> tuple[list[float], float]:
        """Compute the hidden activations and the output for one input."""
        hidden = [sigmoid(self.b1[j] + self.w1[j][0] * x[0] + self.w1[j][1] * x[1]) for j in range(2)]
        output = sigmoid(self.b2 + self.w2[0] * hidden[0] + self.w2[1] * hidden[1])
        return hidden, output

    def train(self, epochs: int, learning_rate: float) -> list[float]:
        """Train with online backpropagation. Return the loss recorded every 2000 epochs."""
        history: list[float] = []
        for epoch in range(1, epochs + 1):
            for x, target in XOR_DATA:
                hidden, output = self.forward(x)
                d_output = (output - target) * output * (1.0 - output)
                d_hidden = [d_output * self.w2[j] * hidden[j] * (1.0 - hidden[j]) for j in range(2)]
                for j in range(2):
                    self.w2[j] -= learning_rate * d_output * hidden[j]
                self.b2 -= learning_rate * d_output
                for j in range(2):
                    self.w1[j][0] -= learning_rate * d_hidden[j] * x[0]
                    self.w1[j][1] -= learning_rate * d_hidden[j] * x[1]
                    self.b1[j] -= learning_rate * d_hidden[j]
            if epoch % 2000 == 0 or epoch == 1:
                loss = sum((self.forward(x)[1] - t) ** 2 for x, t in XOR_DATA) / len(XOR_DATA)
                history.append(loss)
                print(f"  epoch {epoch:5d}: loss {loss:.4f}")
        return history


def main() -> None:
    """Train the two-layer network on XOR and show it solve the problem the perceptron could not."""
    net = TwoLayerNet(seed=1)
    print("training a 2-2-1 network on XOR with backpropagation:\n")
    net.train(epochs=8000, learning_rate=0.5)

    print("\nfinal guesses (rounded to 0 or 1):")
    correct = 0
    for x, target in XOR_DATA:
        output = net.forward(x)[1]
        guess = 1 if output >= 0.5 else 0
        correct += guess == int(target)
        print(f"  {(int(x[0]), int(x[1]))} -> {output:.2f} rounds to {guess}, correct {int(target)}")
    print(f"\naccuracy: {correct}/{len(XOR_DATA)}. One hidden layer, trained by backpropagation,")
    print("learned XOR. This is the step that ended the first winter and opened deep learning.")


if __name__ == "__main__":
    main()
