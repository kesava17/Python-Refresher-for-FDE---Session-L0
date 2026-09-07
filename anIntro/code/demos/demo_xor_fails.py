"""The wall of 1969: a single perceptron cannot learn XOR, no matter how long it trains.

XOR is 1 when the two inputs differ. Its classes are not linearly separable, so the one
straight line a perceptron can draw will always leave a mistake behind. Watch the accuracy
refuse to reach 100 percent. Standard library only.

Run:  poetry run python demo_xor_fails.py
"""

from __future__ import annotations

import random

Example = tuple[tuple[int, int], int]
XOR_DATA: list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]


def predict(x: tuple[int, int], weights: list[float], bias: float) -> int:
    """Return the perceptron's guess for an input."""
    return 1 if bias + weights[0] * x[0] + weights[1] * x[1] >= 0.0 else 0


def accuracy(weights: list[float], bias: float) -> float:
    """Fraction of the XOR examples the perceptron currently gets right."""
    correct = sum(predict(x, weights, bias) == target for x, target in XOR_DATA)
    return correct / len(XOR_DATA)


def main(epochs: int = 50, learning_rate: float = 0.1, seed: int = 1) -> None:
    """Train a single perceptron on XOR and show that it never reaches full accuracy."""
    rng = random.Random(seed)
    weights = [rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)]
    bias = 0.0
    best = 0.0

    for _ in range(1, epochs + 1):
        for x, target in XOR_DATA:
            error = target - predict(x, weights, bias)
            weights[0] += learning_rate * error * x[0]
            weights[1] += learning_rate * error * x[1]
            bias += learning_rate * error
        best = max(best, accuracy(weights, bias))

    print(f"after {epochs} epochs on XOR:")
    print(f"  best accuracy ever reached: {best:.0%}")
    print("  final guesses:")
    for x, target in XOR_DATA:
        print(f"    {x} -> guessed {predict(x, weights, bias)}, correct {target}")

    print("\nThe accuracy never reaches 100 percent. One straight line cannot separate XOR,")
    print("so the perceptron is stuck. This is the limit that froze the field in 1969.")


if __name__ == "__main__":
    main()
