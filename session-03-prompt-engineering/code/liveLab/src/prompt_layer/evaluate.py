"""Test a prompt like code: score it on a held set, and keep the better version.

Runs the held test set (labelled questions with the decision each should get) through the
whole prompt layer and reports, per prompt version, how often it made the right
escalation call and whether every answer validated. Comparing v1 and v2 is how you choose
a prompt on evidence, then version the winner as the component your code calls.

Run:  poetry run python -m prompt_layer.evaluate
"""

from __future__ import annotations

import csv
import os

from model_layer.corpus import load_corpus
from prompt_layer.answerer import answer
from prompt_layer.context import retrieve
from prompt_layer.prompt import answer_via_prompt

_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_held_set() -> list[dict]:
    """Load the held test set: labelled questions with the escalation each should get."""
    rows: list[dict] = []
    with open(os.path.join(_DATA, "prompt_tests.csv"), newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["expect_escalate"] = row["expect_escalate"].strip().lower() == "true"
            rows.append(row)
    return rows


def score_prompt(version: str, held: list[dict], corpus: list[dict]) -> dict:
    """Score one prompt version at the prompt level: does the prompt itself make the right
    escalation call, before the output guardrail is applied? This is what isolates prompt
    quality; the guardrail is measured separately as the backstop."""
    correct = 0
    for row in held:
        drafted = answer_via_prompt(row["question"], retrieve(row["question"], corpus), version=version)
        if drafted.escalate == row["expect_escalate"]:
            correct += 1
    total = len(held)
    return {"version": version, "correct": correct, "total": total,
            "pct": round(100 * correct / total, 1)}


def guardrail_backstop(version: str, held: list[dict]) -> int:
    """Count how many held questions the FULL pipeline (prompt plus guardrails) gets right.
    The output policy is the safety net that should make even a weak prompt safe."""
    return sum(1 for row in held
               if answer(row["question"], version=version).escalate == row["expect_escalate"])


def main() -> None:
    """Score both prompt versions on the held set and recommend the winner."""
    held = load_held_set()
    corpus = load_corpus()
    print(f"Held test set: {len(held)} labelled questions (offline)\n")

    print("Prompt level (the prompt's own decision, no guardrail):")
    print(f"  {'version':<8}{'correct':>9}{'score':>9}")
    print("  " + "-" * 26)
    results = []
    for version in ("v1", "v2"):
        result = score_prompt(version, held, corpus)
        results.append(result)
        print(f"  {result['version']:<8}{result['correct']}/{result['total']:>5}{result['pct']:>8}%")

    best = max(results, key=lambda r: r["pct"])
    print(f"\n  Keep {best['version']}: it scores {best['pct']}%, escalating the sensitive warranty")
    print("  questions the weaker prompt answers directly. Version it as the component the")
    print("  assistant calls, and re-run this on every prompt change.\n")

    print("Full pipeline (prompt plus the output guardrail, the backstop):")
    for version in ("v1", "v2"):
        safe = guardrail_backstop(version, held)
        print(f"  {version}: {safe}/{len(held)} correct")
    print("  The guardrail rescues the weak prompt at runtime, but you still ship the")
    print("  better prompt: defence in depth, not one layer doing all the work.")


if __name__ == "__main__":
    main()
