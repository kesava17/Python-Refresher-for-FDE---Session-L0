"""Assignment 1: run the perceptron on each logic problem and see where the wall is.

Train the same perceptron on AND, OR, and XOR, and print a small table: did it converge, and
what accuracy did it reach. AND and OR are separable and converge; XOR does not.

Run:  poetry run python -m tinynn.experiments
"""

from __future__ import annotations

from tinynn.data import AND, OR, XOR, Example
from tinynn.perceptron import Perceptron


def evaluate(name: str, data: list[Example]) -> None:
    """Train a fresh perceptron on one dataset and print whether it converged and its accuracy."""
    model = Perceptron(seed=1)
    converged = model.fit(data, epochs=200)
    verdict = f"converged at epoch {converged}" if converged > 0 else "never converged"
    print(f"  {name:4s}: {verdict:24s} accuracy {model.accuracy(data):.0%}")


def main() -> None:
    """Compare the perceptron across AND, OR, and XOR."""
    print("a single perceptron across three logic problems:\n")
    evaluate("AND", AND)
    evaluate("OR", OR)
    evaluate("XOR", XOR)
    print("\nAND and OR are linearly separable, so the perceptron learns them. XOR is not, so")
    print("no straight line ever separates it and the perceptron stays below 100 percent.")


if __name__ == "__main__":
    main()
