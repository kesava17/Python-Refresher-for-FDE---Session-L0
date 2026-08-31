"""Demo: the offline model behind a single interface.

Every build in this course runs with no API key. A deterministic mock stands in for
a real model behind the same small interface: generate(prompt). Later you point the
same interface at a real or on-prem model with an env var, and the caller does not
change.

Run:  poetry run python mock_model.py
"""

from __future__ import annotations

from mocklib import generate

QUESTIONS = [
    "Where is my order SE-1024?",
    "How do I return an item?",
    "Is it under warranty?",
]


def main() -> None:
    """Run the offline mock model over the sample questions and print each answer."""
    print("Offline mock model. No key, no network, no cost. Same output every run.\n")
    for q in QUESTIONS:
        print(f"Q: {q}")
        print(f"A: {generate(q)}\n")

    print("The warranty question is answered cautiously and would be escalated to a")
    print("human in the real assistant. That guardrail is built in Session 3.")
    print()
    print("Swap in a real model later with MODEL=real and a key; this caller stays the same.")


if __name__ == "__main__":
    main()
