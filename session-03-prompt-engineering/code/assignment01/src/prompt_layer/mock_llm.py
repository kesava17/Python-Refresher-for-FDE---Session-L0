"""The offline model for assignment 1 (STARTER), with a flaky prompt to repair.

``draft`` is what the model returns for each topic. It has a bug: the return-topic answer
forgets to attach its citation, so a non-escalated answer arrives with no source and fails
the ``Answer`` validator. Repairing this flaky prompt is the first half of the assignment.
It also does not tag the answer with a ``topic`` yet; that is the second half.
"""

from __future__ import annotations

# A tiny fixed corpus, so answers have a source to cite (no retrieval here; that is
# Session 4). Each answerable topic has one help doc.
_DOC = {
    "order": ("HC-001", "Track your order in My Orders using the tracking link or the order id."),
    "return": ("HC-003", "Start a return from My Orders; a prepaid label is emailed to you."),
}


def classify(question: str) -> str:
    """Return the coarse topic: order, return, warranty, or out_of_scope."""
    q = question.lower()
    if "warrant" in q:
        return "warranty"
    if "return" in q or "refund" in q or "exchange" in q:
        return "return"
    if "order" in q or "track" in q or "deliver" in q or "cancel" in q or "arriv" in q:
        return "order"
    return "out_of_scope"


def draft(question: str) -> dict:
    """Return the fields of an Answer for the question. STARTER: contains the flaky bug."""
    topic = classify(question)
    if topic == "order":
        doc_id, body = _DOC["order"]
        return {"answer": body, "citations": [doc_id], "confidence": "high",
                "escalate": False, "reason": "answered from order help content"}
    if topic == "return":
        doc_id, body = _DOC["return"]
        # BUG (repair me): a confident, non-escalated answer with no citation. The prompt
        # forgot to pass the source through, so this fails the Answer validator.
        return {"answer": body, "citations": [], "confidence": "high",
                "escalate": False, "reason": "answered from return help content"}
    if topic == "warranty":
        return {"answer": "This is a warranty question. A Sunrise support agent will confirm your status.",
                "citations": [], "confidence": "low", "escalate": True,
                "reason": "warranty is legally sensitive and always routes to a human"}
    return {"answer": "I cannot answer that from Sunrise help content. I will pass you to a support agent.",
            "citations": [], "confidence": "low", "escalate": True,
            "reason": "out of scope for the help content"}
