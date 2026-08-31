"""Assignment 1 starter: compare three model configurations and defend a pick.

Fill in THREE candidates below, run this, read the scores, and write your one-paragraph
recommendation at the bottom. Everything runs offline (no API key). Full brief in
assignment-01.md.

Run:  poetry run python my_comparison.py
"""

from __future__ import annotations

from model_layer.compare import score
from model_layer.corpus import load_golden

# TODO: define THREE candidates to compare. Each is (model_name, profile).
# model_name must be one the factory knows (mock-small, mock-medium, mock-large, or a
# new one you add in model_layer/model.py). Fill the profile with realistic numbers,
# and remember: a candidate that cannot run in Bharat is disqualified, whatever it scores.
CANDIDATES: list[tuple[str, dict]] = [
    # ("mock-small",  {"cost_per_1k": 0.10, "latency_ms": 200,  "in_bharat": True}),
    # ("mock-medium", {"cost_per_1k": 0.50, "latency_ms": 500,  "in_bharat": True}),
    # ("mock-large",  {"cost_per_1k": 2.00, "latency_ms": 1200, "in_bharat": True}),
]


def main() -> None:
    """Score the chosen candidates against the golden set and print their results."""
    if not CANDIDATES:
        print("Add three candidates to CANDIDATES, then run again.")
        return
    golden = load_golden()
    print(f"{'model':<14}{'score':>7}{'answered':>12}{'escalated':>12}   profile")
    print("-" * 70)
    for name, profile in CANDIDATES:
        r = score(name, golden)
        print(f"{name:<14}{r['score']:>6}%{r['answered']:>12}{r['escalated']:>12}   {profile}")

    # TODO: write your recommendation here (or in assignment-01.md):
    #   Which candidate, and why? Weigh capability on the golden set, cost, latency,
    #   Bharat residency (a hard gate), and clean warranty escalation (a hard gate).


if __name__ == "__main__":
    main()
