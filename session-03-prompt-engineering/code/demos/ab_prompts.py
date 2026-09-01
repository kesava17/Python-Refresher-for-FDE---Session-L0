"""Demo 8: test a prompt like code, and keep the better one.

Two prompts, one held test set, one number each. A weak prompt and a strict prompt are
scored on a small labelled set: does each question get the decision it should (answer the
answerable ones, escalate the sensitive and out-of-scope ones)? You do not argue about
which prompt is better; you read the score and keep the winner.

Run:  poetry run python ab_prompts.py
"""

from __future__ import annotations

from promptlib import draft, retrieve


# A small held set: the question and the decision it should get. Drawn from the golden set.
HELD_SET = [
    ("How do I return an item?", False),
    ("Where is my order SE-100234?", False),
    ("When will I get my refund?", False),
    ("Is my product under warranty?", True),
    ("My warranty claim was rejected", True),
    ("Can I get a discount coupon?", True),
    ("What is the wifi password at the Pune office?", True),
]

PROMPTS = {
    "v1 (weak: help with anything)": "loose",
    "v2 (strict: scope + escalation)": "strict",
}


def score(policy: str) -> tuple[int, int]:
    """Run the held set under one policy; return (correct decisions, total)."""
    correct = 0
    for question, should_escalate in HELD_SET:
        result = draft(question, retrieve(question), policy=policy)
        if result["escalate"] == should_escalate:
            correct += 1
    return correct, len(HELD_SET)


def main() -> None:
    """Score both prompts on the held set and recommend the winner."""
    print(f"held set: {len(HELD_SET)} labelled questions\n")
    results = {}
    for label, policy in PROMPTS.items():
        correct, total = score(policy)
        pct = round(100 * correct / total)
        results[label] = pct
        print(f"  {label:<34} {correct}/{total}  ({pct}%)")

    winner = max(results, key=results.get)
    print(f"\nKeep {winner}: it makes the right escalation decision more often.")
    print("This is how a prompt is tuned: change it, run the held set, read the number,")
    print("and only ship the version that scores higher. Regression testing for prompts.")


if __name__ == "__main__":
    main()
