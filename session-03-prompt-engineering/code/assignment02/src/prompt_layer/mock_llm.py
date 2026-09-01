"""The offline model for assignment 2. Answers order and return, escalates the rest."""

from __future__ import annotations

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
    """Return the fields of an Answer for the question, grounded for answerable topics."""
    topic = classify(question)
    if topic in ("order", "return"):
        doc_id, body = _DOC[topic]
        return {"answer": body, "citations": [doc_id], "confidence": "high",
                "escalate": False, "reason": f"answered from {topic} help content"}
    if topic == "warranty":
        return {"answer": "This is a warranty question. A Sunrise support agent will confirm your status.",
                "citations": [], "confidence": "low", "escalate": True,
                "reason": "warranty is legally sensitive and always routes to a human"}
    return {"answer": "I cannot answer that from Sunrise help content. I will pass you to a support agent.",
            "citations": [], "confidence": "low", "escalate": True,
            "reason": "out of scope for the help content"}
