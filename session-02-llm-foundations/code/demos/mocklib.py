"""Tiny offline stand-ins for a language model, so the demos run with no API key.

Everything here is deterministic and dependency-free (standard library only). It is
NOT a real model. It is just enough behaviour to make the foundations visible:
tokenizing, a canned next-token distribution, a deterministic answer, and a simple
meaning vector for embeddings. The point of the demos is the concept, not the model.
"""

from __future__ import annotations

import hashlib
import math
import re

# Illustrative price, in Rs per 1,000 tokens, so the cost demo has a number.
PRICE_PER_1K = 0.50


def tokenize(text: str) -> list[str]:
    """Approximate a tokenizer: words and punctuation, with long words split into
    roughly four-character pieces (real tokenizers do something like this)."""
    raw = re.findall(r"\w+|[^\w\s]", text)
    toks: list[str] = []
    for w in raw:
        if w.isalnum() and len(w) > 6:
            for i in range(0, len(w), 4):
                toks.append(w[i:i + 4])
        else:
            toks.append(w)
    return toks


def count_tokens(text: str) -> int:
    """Count the tokens in a string. A model bills for input tokens plus output tokens."""
    return len(tokenize(text))


def estimate_cost(n_tokens: int, price_per_1k: float = PRICE_PER_1K) -> float:
    """Estimate the cost of a call, in rupees, from its token count and the price per 1,000 tokens."""
    return n_tokens / 1000 * price_per_1k


# A small canned next-token table, keyed by how the context ends. Deterministic.
_NEXT: dict[str, list[tuple[str, float]]] = {
    "where is my": [("order", 0.68), ("package", 0.14), ("refund", 0.10), ("delivery", 0.08)],
    "how do i": [("return", 0.55), ("cancel", 0.20), ("track", 0.15), ("contact", 0.10)],
    "is it under": [("warranty", 0.90), ("guarantee", 0.06), ("cover", 0.04)],
    "i want to": [("return", 0.50), ("cancel", 0.28), ("check", 0.22)],
    "my order": [("status", 0.45), ("number", 0.30), ("is", 0.25)],
}


def next_token_probs(context: str) -> list[tuple[str, float]]:
    """Return a canned distribution over the next token for a given context."""
    low = context.lower().strip()
    tail = " ".join(tokenize(low)[-3:])
    for key, dist in _NEXT.items():
        if tail.endswith(key) or low.endswith(key):
            return dist
    return [(".", 0.40), ("?", 0.30), ("please", 0.20), ("now", 0.10)]


def generate(prompt: str) -> str:
    """A deterministic, templated answer. Same prompt, same answer, every time."""
    p = prompt.lower()
    if "return" in p or "refund" in p:
        return ("To return an item, open My Orders, choose the item, and select Return. "
                "A prepaid label is emailed to you.")
    if "where" in p and "order" in p:
        return "Track your order in My Orders with the tracking link, or by the order id."
    if "warranty" in p:
        return ("This is a warranty question. A human agent will confirm the warranty "
                "status for you.")
    return "I can help with order status, returns, and warranty questions."


def embed(text: str, dim: int = 16) -> list[float]:
    """A cheap deterministic meaning vector: hash tokens into buckets, then normalise.
    Similar texts share tokens, so their vectors sit close together."""
    vec = [0.0] * dim
    for tok in tokenize(text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 4) for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors: near 1.0 means similar meaning, near 0.0 means unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return round(dot / (na * nb), 3)
