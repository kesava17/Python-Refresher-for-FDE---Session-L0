"""Demo 2: assemble a context, and respect a token budget.

The context window is a budget, not an inbox. You cannot pour everything in: the
instructions, the retrieved passages, and room for the answer all have to fit. This demo
assembles a context, prices each part in tokens, and trims the least relevant passage
when the budget is tight. Order matters too: the rules first, the sources next.

Run:  poetry run python context_build.py
"""

from __future__ import annotations

from promptlib import estimate_tokens


SYSTEM = "You are Sunrise Support. Answer order, return, and warranty questions from the context."

# Candidate passages, most relevant first (a real retriever ranks these; here they are fixed).
PASSAGES = [
    ("HC-003", "Start a return from My Orders; a prepaid label is emailed to you."),
    ("HC-004", "Refunds are issued in 5 to 7 business days after we receive the item."),
    ("KB-101", "Opened earphones cannot be returned for hygiene reasons."),
    ("KB-105", "To change size, return the item and place a fresh order for the size you want."),
]


def assemble(passages: list[tuple[str, str]], budget: int, answer_room: int = 40) -> tuple[str, int]:
    """Fit the system prompt and as many passages as the budget allows, keeping room for
    the answer. Returns the assembled context and the tokens it uses."""
    used = estimate_tokens(SYSTEM)
    lines = [SYSTEM, "", "Context:"]
    for doc_id, body in passages:
        cost = estimate_tokens(f"[{doc_id}] {body}")
        if used + cost > budget - answer_room:
            print(f"  drop [{doc_id}] ({cost} tokens): would exceed the budget")
            continue
        used += cost
        lines.append(f"[{doc_id}] {body}")
    return "\n".join(lines), used


def main() -> None:
    """Assemble the same passages under a generous budget and a tight one."""
    total = sum(estimate_tokens(f"[{d}] {b}") for d, b in PASSAGES) + estimate_tokens(SYSTEM)
    print(f"all passages plus the system prompt cost {total} tokens\n")

    print("budget 200 tokens (generous): everything fits")
    context, used = assemble(PASSAGES, budget=200)
    print(f"  used {used} tokens\n")

    print("budget 70 tokens (tight): keep the most relevant, drop the rest")
    context, used = assemble(PASSAGES, budget=70, answer_room=15)
    print(f"  used {used} tokens")
    print(f"  kept:\n{context}\n")

    print("A budget forces a choice: rank the passages, keep the ones that answer the")
    print("question, and always leave room for the model to reply. This is why Session 4")
    print("retrieves only the few passages that matter instead of sending the whole corpus.")


if __name__ == "__main__":
    main()
