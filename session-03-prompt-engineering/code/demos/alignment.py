"""Demo 3: the system prompt is policy, and it keeps the model on task.

Alignment is engineered, not hoped for. The same off-scope question, under a weak system
prompt versus a strict one, gives two very different behaviours: the weak prompt guesses
(and would fail our validator, because a non-escalated answer with no citation is not
allowed), while the strict prompt refuses and hands off to a human. The context decides
what the model will and will not do.

Run:  poetry run python alignment.py
"""

from __future__ import annotations

from promptlib import draft, retrieve


WEAK = "You are a friendly assistant. Try to help with anything the user asks."
STRICT = (
    "You are Sunrise Support. Scope: order, return, and warranty only. Answer strictly "
    "from the provided context. If the question is out of scope or the context does not "
    "cover it, do not guess: set escalate=true and hand off to a human."
)

QUESTIONS = [
    "How do I return an item?",          # in scope: both prompts answer
    "Can I get a discount coupon?",       # out of scope: only the strict prompt escalates
]


def run(policy_label: str, policy: str) -> None:
    """Answer every sample question under one policy and print the decision."""
    print(f"--- system prompt: {policy_label} ---")
    for q in QUESTIONS:
        result = draft(q, retrieve(q), policy=policy)
        flag = "ESCALATE to human" if result["escalate"] else "answered by bot"
        print(f"  Q: {q}")
        print(f"     {flag}: {result['answer']}")
    print()


def main() -> None:
    """Contrast a weak and a strict system prompt on the same questions."""
    run("weak (help with anything)", policy="loose")
    run("strict (scope + escalation rule)", policy="strict")

    print("Same model, same questions, opposite behaviour on the out-of-scope case.")
    print("The strict prompt is the alignment: it turns 'be careful' into a rule the")
    print("model follows every time, and it is what routes the sensitive cases to a human.")


if __name__ == "__main__":
    main()
