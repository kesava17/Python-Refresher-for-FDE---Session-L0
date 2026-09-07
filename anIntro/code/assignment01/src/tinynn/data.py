"""The classic logic datasets used through the lab: AND, OR, and XOR.

Each is four examples: a pair of 0/1 inputs and the correct 0/1 output. AND and OR are
linearly separable (a perceptron can learn them); XOR is not (it needs a hidden layer).
"""

from __future__ import annotations

Example = tuple[tuple[int, int], int]

AND: list[Example] = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
OR: list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
XOR: list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
