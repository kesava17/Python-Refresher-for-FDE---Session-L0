"""Assignment 2: cross the wall, and see how hidden-layer size changes what XOR needs.

Train the two-layer network on XOR with different numbers of hidden neurons and print the
accuracy and loss for each. One hidden neuron is not enough; two or more can solve XOR.

Run:  poetry run python -m tinynn.experiments
"""

from __future__ import annotations

from tinynn.data import XOR
from tinynn.mlp import TwoLayerNet


def evaluate(hidden: int) -> None:
    """Train a network with the given hidden size on XOR and print its accuracy and loss."""
    net = TwoLayerNet(hidden=hidden, seed=1)
    net.fit(XOR)
    print(f"  hidden = {hidden}: accuracy {net.accuracy(XOR):.0%}, loss {net.loss(XOR):.4f}")


def main() -> None:
    """Compare hidden-layer sizes on XOR."""
    print("a two-layer network on XOR, varying the hidden-layer size:\n")
    for hidden in (1, 2, 4):
        evaluate(hidden)
    print("\nOne hidden neuron cannot bend the boundary enough for XOR. Two is the classic")
    print("minimum, and more hidden neurons make training easier and more reliable.")


if __name__ == "__main__":
    main()
