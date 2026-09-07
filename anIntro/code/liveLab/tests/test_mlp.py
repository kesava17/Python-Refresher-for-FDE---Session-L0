"""Tests for the two-layer network: it learns XOR and its loss falls while training."""

from __future__ import annotations

from tinynn.data import XOR
from tinynn.mlp import TwoLayerNet, sigmoid


def test_sigmoid_range() -> None:
    """Sigmoid maps 0 to 0.5 and is bounded between 0 and 1."""
    assert sigmoid(0.0) == 0.5
    assert 0.0 < sigmoid(-10.0) < sigmoid(10.0) < 1.0


def test_learns_xor() -> None:
    """After training, the two-layer network classifies all of XOR correctly."""
    net = TwoLayerNet(hidden=2, seed=1)
    net.fit(XOR)
    assert net.accuracy(XOR) == 1.0


def test_loss_decreases() -> None:
    """Training reduces the loss substantially from its starting value."""
    net = TwoLayerNet(hidden=2, seed=1)
    before = net.loss(XOR)
    net.fit(XOR)
    after = net.loss(XOR)
    assert after < before
    assert after < 0.05
