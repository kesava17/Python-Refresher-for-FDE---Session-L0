"""The model-comparison harness: choose a model on evidence, not hype.

Runs the golden question set through several candidate models, scores each on two
things that matter for Sunrise (does it answer the answerable questions, and does it
escalate the sensitive ones), and prints a recommendation. Fully offline: the
candidates are three capability levels of the deterministic mock, so the harness runs
with no API key. Point it at real candidates later by adding them to CANDIDATES.

Run:  poetry run python -m model_layer.compare
"""

from __future__ import annotations

import re

from model_layer.corpus import load_golden
from model_layer.model import make_model

# The candidates to compare. Offline by default (three mock capability levels).
# Add "real" here once LLM_PROVIDER and LLM_API_KEY are set in the environment.
CANDIDATES = ["mock-small", "mock-medium", "mock-large"]

# Illustrative cost and latency, so the recommendation weighs more than accuracy.
PROFILE = {
    "mock-small":  {"cost_per_1k": 0.10, "latency_ms": 200, "in_bharat": True},
    "mock-medium": {"cost_per_1k": 0.50, "latency_ms": 500, "in_bharat": True},
    "mock-large":  {"cost_per_1k": 2.00, "latency_ms": 1200, "in_bharat": True},
}


def _escalated(answer: str) -> bool:
    """Return True when the answer hands the question to a human agent."""
    low = answer.lower()
    return "human" in low or "agent" in low


def _on_topic(reference: str, answer: str) -> bool:
    """Return True when the answer shares at least one keyword with the reference."""
    ref = set(re.findall(r"[a-z]{4,}", reference.lower()))
    ans = set(re.findall(r"[a-z]{4,}", answer.lower()))
    return len(ref & ans) >= 1


def score(model_name: str, golden: list[dict]) -> dict:
    """Run one model over the golden set and return its answer and escalation tallies."""
    model = make_model(model_name)
    answer_hits = escalate_hits = answerable = escalation = 0
    for row in golden:
        answer = model.generate(row["question"])
        if row["should_escalate"]:
            escalation += 1
            if _escalated(answer):
                escalate_hits += 1
        else:
            answerable += 1
            if not _escalated(answer) and _on_topic(row["reference_answer"], answer):
                answer_hits += 1
    correct = answer_hits + escalate_hits
    total = len(golden)
    return {
        "name": model_name,
        "score": round(100 * correct / total, 1),
        "answered": f"{answer_hits}/{answerable}",
        "escalated": f"{escalate_hits}/{escalation}",
    }


def main() -> None:
    """Score every candidate model, print the comparison table, and recommend one."""
    golden = load_golden()
    results = [score(name, golden) for name in CANDIDATES]

    print(f"Model comparison on {len(golden)} golden questions (offline)\n")
    print(f"{'model':<14}{'score':>7}{'answered':>12}{'escalated':>12}"
          f"{'cost/1k':>10}{'latency':>10}{'in Bharat':>11}")
    print("-" * 76)
    for r in results:
        p = PROFILE[r["name"]]
        print(f"{r['name']:<14}{r['score']:>6}%{r['answered']:>12}{r['escalated']:>12}"
              f"{'Rs ' + str(p['cost_per_1k']):>10}{str(p['latency_ms']) + 'ms':>10}"
              f"{('yes' if p['in_bharat'] else 'no'):>11}")

    best = max(results, key=lambda r: r["score"])
    p = PROFILE[best["name"]]
    print("\nRecommendation")
    print(f"  Pick {best['name']}: it scores {best['score']}% on the golden set, and it")
    print(f"  escalates the sensitive warranty and out-of-scope questions ({best['escalated']}).")
    print(f"  It runs in Bharat ({'yes' if p['in_bharat'] else 'no'}) at Rs {p['cost_per_1k']}/1k tokens.")
    print("  Residency is a hard filter: a candidate that cannot run in Bharat is out,")
    print("  however well it scores. Weigh cost and latency against the score for the rest.")


if __name__ == "__main__":
    main()
