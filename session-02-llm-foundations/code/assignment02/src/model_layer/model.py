"""The model layer: one small interface, a pluggable model behind it.

The rest of the assistant never cares which model answers. It calls two methods,
`generate` and `embed`, on whatever `make_model()` returns. Today that is a
deterministic offline mock (no API key, no network). Later a real or on-prem model
plugs in behind the same interface, selected by the `LLM_MODEL` environment variable,
with its key read from the environment and never written in code.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Protocol


class Model(Protocol):
    """Every model, mock or real, honours this contract."""

    name: str

    def generate(self, prompt: str) -> str:
        """Return the model's text answer to the prompt."""
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one meaning vector per input text."""
        ...


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase word and punctuation tokens."""
    return re.findall(r"\w+|[^\w\s]", text.lower())


def _classify(question: str) -> str:
    """Return the coarse topic of a question: order, return, warranty, or out_of_scope."""
    q = question.lower()
    if "warrant" in q:
        return "warranty"
    if "return" in q or "refund" in q or "exchange" in q:
        return "return"
    if "order" in q or "track" in q or "deliver" in q or "arriv" in q or "cancel" in q:
        return "order"
    return "out_of_scope"


class MockModel:
    """A deterministic stand-in for a real model.

    The `capability` level changes how well it handles the two hard cases (warranty,
    which is sensitive and should go to a human, and questions not in scope). This is
    what makes the comparison harness meaningful offline: a weaker model escalates
    less reliably, and scores lower.
    """

    def __init__(self, capability: str = "medium") -> None:
        """Create a mock model at the given capability level."""
        self.capability = capability
        self.name = f"mock-{capability}"

    def generate(self, prompt: str) -> str:
        """Return a canned answer for the prompt's topic, escalating sensitive cases."""
        topic = _classify(prompt)
        if topic == "order":
            return "Track your order in My Orders using the tracking link or the order id."
        if topic == "return":
            return "Open My Orders, choose the item, and select Return. A prepaid label is emailed to you."
        if topic == "warranty":
            # A capable model does not decide a sensitive warranty case; it escalates.
            if self.capability in ("medium", "large"):
                return "This is a warranty question. A human agent will confirm your warranty status."
            return "Yes, most products carry a one-year warranty."  # weak model over-answers
        # out of scope
        if self.capability == "large":
            return "I cannot answer that from our help content. I will pass you to a human agent."
        return "I think that should be fine."  # weak/medium model makes something up

    def embed(self, texts: list[str], dim: int = 32) -> list[list[float]]:
        """Return a deterministic normalized hash vector for each input text."""
        out: list[list[float]] = []
        for text in texts:
            vec = [0.0] * dim
            for tok in _tokenize(text):
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                vec[h % dim] += 1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            out.append([round(v / norm, 5) for v in vec])
        return out


class RealModel:
    """Adapter seam for a real or on-prem model. Offline by default: this is not
    wired to a provider here. It reads its configuration from the environment so no
    secret ever lives in the repo, and it fails loudly if asked to run unconfigured."""

    def __init__(self) -> None:
        """Read provider and key from the environment without failing if unset."""
        self.name = "real"
        self.provider = os.environ.get("LLM_PROVIDER", "")
        self.api_key = os.environ.get("LLM_API_KEY", "")

    def _require(self) -> None:
        """Raise a clear error if the provider or key is not configured."""
        if not self.provider or not self.api_key:
            raise RuntimeError(
                "Real model not configured. Set LLM_PROVIDER and LLM_API_KEY in the "
                "environment, or use the offline mock (the default)."
            )

    def generate(self, prompt: str) -> str:
        """Generate an answer via the real provider once wired and configured."""
        self._require()
        raise NotImplementedError("Wire your provider's SDK call here, reading the key from the environment.")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts via the real provider once wired and configured."""
        self._require()
        raise NotImplementedError("Wire your provider's embeddings call here.")


def make_model(name: str | None = None) -> Model:
    """Return a model by name. Defaults to the offline mock so nothing is ever blocked.

    Names: mock, mock-small, mock-medium, mock-large, real.
    If `name` is None, read the `LLM_MODEL` environment variable (default `mock`).
    """
    chosen = (name or os.environ.get("LLM_MODEL", "mock")).strip().lower()
    if chosen in ("mock", "mock-medium"):
        return MockModel("medium")
    if chosen == "mock-small":
        return MockModel("small")
    if chosen == "mock-large":
        return MockModel("large")
    if chosen == "real":
        return RealModel()
    raise ValueError(f"Unknown model '{chosen}'. Try mock, mock-small, mock-large, or real.")
