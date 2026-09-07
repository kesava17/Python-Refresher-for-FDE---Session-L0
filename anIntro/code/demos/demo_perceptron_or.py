"""Train a perceptron on OR, from scratch, with Rosenblatt's 1958 learning rule.

Watch the machine learn the weights from examples: start from random weights, adjust them a
little on every mistake, and converge to weights that classify OR correctly. This is learning
by adjusting connection strengths, the one idea behind everything. Standard library only.

Run:  poetry run python demo_perceptron_or.py
"""

from __future__ import annotations

import random

Example = tuple[tuple[int, int], int]
OR_DATA: list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]


def predict(x: tuple[int, int], weights: list[float], bias: float) -> int:
    """Return the perceptron's guess: 1 if the weighted sum is at least zero, else 0."""
    return 1 if bias + weights[0] * x[0] + weights[1] * x[1] >= 0.0 else 0


def accuracy(weights: list[float], bias: float) -> float:
    """Fraction of the OR examples the perceptron currently gets right."""
    correct = sum(predict(x, weights, bias) == target for x, target in OR_DATA)
    return correct / len(OR_DATA)


def train(epochs: int = 10, learning_rate: float = 0.1, seed: int = 1) -> None:
    """Run the perceptron learning rule over OR and report progress each epoch."""
    rng = random.Random(seed)
    weights = [rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)]
    bias = 0.0
    print(f"start: weights [{weights[0]:.2f}, {weights[1]:.2f}], bias {bias:.2f}\n")

    for epoch in range(1, epochs + 1):
        mistakes = 0
        for x, target in OR_DATA:
            error = target - predict(x, weights, bias)
            if error != 0:
                mistakes += 1
                weights[0] += learning_rate * error * x[0]
                weights[1] += learning_rate * error * x[1]
                bias += learning_rate * error
        print(f"  epoch {epoch:2d}: {mistakes} mistake(s), accuracy {accuracy(weights, bias):.0%}")
        if mistakes == 0:
            print(f"\nconverged: weights [{weights[0]:.2f}, {weights[1]:.2f}], bias {bias:.2f}")
            print("The perceptron found a straight line that separates OR. It learned, from")
            print("examples alone, weights nobody set by hand.")
            return

    print("\ndid not converge in the epochs allowed")


def main() -> None:
    """Train a perceptron on OR and show it converge."""
    train()


if __name__ == "__main__":
    main()
