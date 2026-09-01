"""Demo 4: free text is fragile; a validated object is not.

The same answer, two ways. First as free text: a human can read it, but code cannot
trust it. Then as a pydantic ``Answer``: the fields are typed, present, and checked, so
the next layer can branch on ``escalate`` and read ``citations`` without guessing or
string-scraping.

Run:  poetry run python freeform_vs_schema.py "How do I return an item?"
"""

from __future__ import annotations

import sys

from promptlib import Answer, complete_json, retrieve


def main() -> None:
    """Show a free-text answer, then the same content as a validated Answer object."""
    question = sys.argv[1] if len(sys.argv) > 1 else "How do I return an item?"
    passages = retrieve(question)

    print(f'question: "{question}"\n')

    # Free text: readable, but the calling code has to guess the structure.
    free_text = "Sure! Just go to My Orders and start a return. A label will be emailed. (source: HC-003)"
    print("FREE TEXT (what a plain prompt returns):")
    print(f"    {free_text}")
    print("    To act on this, code must scrape the source out of the sentence and hope")
    print("    the wording never changes. Fragile.\n")

    # Structured: the model is asked for JSON, we parse it and validate to the contract.
    raw = complete_json(question, passages)
    answer = Answer.model_validate_json(raw)
    print("STRUCTURED (prompt-for-JSON, validated to the Answer contract):")
    print(f"    {answer.model_dump()}")
    print(f"    code can now do:  if answer.escalate: handoff()   else: show(answer.citations)")
    print(f"    escalate={answer.escalate}   confidence={answer.confidence}   citations={answer.citations}")


if __name__ == "__main__":
    main()
