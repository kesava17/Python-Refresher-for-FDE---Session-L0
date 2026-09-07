"""Gradient descent: how a network actually moves its weights downhill.

Backpropagation says which way is downhill; gradient descent takes the steps. Here we walk
down a simple error curve and watch the learning rate decide whether we glide to the bottom or
bounce out. Standard library only.

Run:  poetry run python demo_gradient_descent.py
"""

from __future__ import annotations


def error(x: float) -> float:
    """A simple bowl-shaped error curve with its lowest point at x = 3."""
    return (x - 3.0) ** 2


def gradient(x: float) -> float:
    """The slope of the error curve: which way is uphill, and how steep."""
    return 2.0 * (x - 3.0)


def descend(start: float, learning_rate: float, steps: int) -> None:
    """Step downhill from a starting point and print the position and error each step."""
    x = start
    for step in range(1, steps + 1):
        x = x - learning_rate * gradient(x)
        print(f"  step {step}: x = {x:6.2f}, error = {error(x):8.2f}")


def main() -> None:
    """Contrast a sensible learning rate with one that is too large."""
    print("The lowest error is at x = 3. We start at x = 0 and step downhill.\n")

    print("learning rate 0.1 (sensible): glides toward the bottom")
    descend(start=0.0, learning_rate=0.1, steps=6)

    print("\nlearning rate 1.1 (too large): overshoots and flies apart")
    descend(start=0.0, learning_rate=1.1, steps=6)

    print("\nThe step size is the learning rate. Too small and training crawls; too large and")
    print("it diverges. Choosing it well is a core part of training any network.")


if __name__ == "__main__":
    main()
