"""Run the whole story end to end, so the lab has one command that shows it all.

Run:  poetry run python -m tinynn.run
"""

from __future__ import annotations

from tinynn.data import OR, XOR
from tinynn.mlp import TwoLayerNet
from tinynn.perceptron import Perceptron


def main() -> None:
    """Train a perceptron on OR (learns), on XOR (fails), then a two-layer net on XOR (learns)."""
    perceptron_or = Perceptron(seed=1)
    converged = perceptron_or.fit(OR)
    print(f"perceptron on OR : converged at epoch {converged}, accuracy {perceptron_or.accuracy(OR):.0%}")

    perceptron_xor = Perceptron(seed=1)
    perceptron_xor.fit(XOR, epochs=50)
    print(f"perceptron on XOR: accuracy {perceptron_xor.accuracy(XOR):.0%}, it cannot reach 100 percent")

    net = TwoLayerNet(hidden=2, seed=1)
    net.fit(XOR)
    print(f"two-layer on XOR : accuracy {net.accuracy(XOR):.0%}, loss {net.loss(XOR):.4f}")
    print("\nThe single line fails on XOR; the hidden layer, trained by backpropagation, solves it.")


if __name__ == "__main__":
    main()
