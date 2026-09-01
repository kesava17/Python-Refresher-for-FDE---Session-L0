"""Demo 1: the parts of a prompt, and how each part changes the answer.

A prompt is not one blob of text. It has parts: a system or role line, the
instructions, a slot for context, and few-shot examples. This demo builds a prompt up
one part at a time and shows the answer getting more reliable as the parts arrive: the
grounded, cited answer only appears once the context slot is filled.

Run:  poetry run python prompt_parts.py "How do I return an item?"
"""

from __future__ import annotations

import sys

from promptlib import complete_toolcall, retrieve


SYSTEM = "You are Sunrise Support. Answer only order, return, and warranty questions."
INSTRUCTIONS = "Answer from the provided context only. If it is not there, escalate to a human."
FEW_SHOT = 'Example -> Q: "Where is my order?"  A: cite HC-001, do not guess.'


def show(label: str, prompt_text: str, question: str, passages: list[dict]) -> None:
    """Print one assembled prompt and the structured answer it produces.

    The model answers the ``question`` grounded in ``passages``; ``prompt_text`` is only
    what we display, so the reader sees the prompt growing part by part.
    """
    result = complete_toolcall(question, passages)
    print(f"--- {label} ---")
    print(prompt_text.strip())
    print(f"  -> answer:    {result['answer']}")
    print(f"  -> citations: {result['citations']}   escalate: {result['escalate']}\n")


def main() -> None:
    """Build a prompt part by part and show each version's answer for one question."""
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I return an item?"
    passages = retrieve(question)

    print(f'question: "{question}"\n')

    # Role only: no instructions, no context. The model has little to work with.
    show("role only", f"{SYSTEM}\n\nQ: {question}", question, passages=[])

    # Add instructions: now it knows the rules, but still has no source to cite.
    show("role + instructions", f"{SYSTEM}\n{INSTRUCTIONS}\n\nQ: {question}", question, passages=[])

    # Add the context slot: now it can ground the answer and cite a real document.
    context = "\n".join(f"[{p['doc_id']}] {p['body']}" for p in passages)
    show("role + instructions + context",
         f"{SYSTEM}\n{INSTRUCTIONS}\n\nContext:\n{context}\n\nQ: {question}", question, passages)

    # Add a few-shot example: the shape of a good answer is now demonstrated, not just told.
    show("role + instructions + context + few-shot",
         f"{SYSTEM}\n{INSTRUCTIONS}\n{FEW_SHOT}\n\nContext:\n{context}\n\nQ: {question}", question, passages)

    print("Each part pulls its weight. The cited answer only appears once the context")
    print("slot is filled: the model can only ground an answer in what you give it.")


if __name__ == "__main__":
    main()
