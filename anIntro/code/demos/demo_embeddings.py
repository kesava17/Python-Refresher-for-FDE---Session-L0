"""Meaning as numbers: words as vectors, and similarity as distance.

The 2013 idea that reshaped language work: represent each word as a short list of numbers,
learned so that words with similar meaning sit close together. Here we hand-build tiny vectors
and measure closeness with cosine similarity. Standard library only.

Run:  poetry run python demo_embeddings.py
"""

from __future__ import annotations

import math

# Hand-made three-number vectors on made-up axes: [royalty, human, fruit].
# Real embeddings are learned and have hundreds of numbers, but the idea is exactly this.
VECTORS: dict[str, list[float]] = {
    "king": [0.9, 0.8, 0.0],
    "queen": [0.9, 0.8, 0.0],
    "man": [0.1, 0.9, 0.0],
    "woman": [0.1, 0.9, 0.0],
    "apple": [0.0, 0.0, 0.9],
}


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity: near 1.0 means similar meaning, near 0.0 means unrelated."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def main() -> None:
    """Show that same-topic words sit close and different-topic words sit far apart."""
    print("each word is a short vector on made-up axes [royalty, human, fruit]:\n")
    for word, vector in VECTORS.items():
        print(f"  {word:6s} {vector}")

    print("\nsimilarity (1.0 = same meaning, 0.0 = unrelated):")
    for a, b in [("king", "queen"), ("king", "man"), ("king", "apple"), ("man", "woman")]:
        print(f"  {a:6s} vs {b:6s} -> {cosine(VECTORS[a], VECTORS[b]):.2f}")

    print("\nWords with similar meaning land close together, unrelated ones far apart. Once")
    print("meaning is geometry, a network can reason about it with arithmetic. This idea sits")
    print("under modern search, translation, and the retrieval that grounds today's assistants.")


if __name__ == "__main__":
    main()
