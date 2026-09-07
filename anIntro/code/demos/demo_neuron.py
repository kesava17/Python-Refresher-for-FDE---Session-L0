"""A single artificial neuron: inputs, weights, a sum, an activation.

The whole field is built from this one unit. Here we compute a neuron's output by hand and
watch how changing its weights and bias changes the decision it makes. Standard library only.

Run:  poetry run python demo_neuron.py
"""

from __future__ import annotations


def step(total: float) -> int:
    """The activation: fire (1) if the weighted sum is at least zero, otherwise 0."""
    return 1 if total >= 0.0 else 0


def neuron(inputs: list[float], weights: list[float], bias: float) -> int:
    """Compute one neuron's output: the weighted sum of inputs plus a bias, through the step."""
    total = bias + sum(w * x for w, x in zip(weights, inputs, strict=True))
    return step(total)


def _truth(weights: list[float], bias: float) -> None:
    """Print the neuron's output for all four two-input combinations."""
    for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        print(f"  ({a}, {b}) -> {neuron([float(a), float(b)], weights, bias)}")


def main() -> None:
    """Show that the same neuron becomes different logic when its weights and bias change."""
    print("A neuron computes: output = step( w1*x1 + w2*x2 + bias )\n")

    print("weights [1, 1], bias -0.5  ->  this neuron behaves like OR:")
    _truth([1.0, 1.0], -0.5)

    print("\nweights [1, 1], bias -1.5  ->  harder to fire, now it behaves like AND:")
    _truth([1.0, 1.0], -1.5)

    print("\nSame unit, different weights and bias, different logic. Learning is nothing more")
    print("than finding the weights and bias that make the neuron decide the way you want.")


if __name__ == "__main__":
    main()
