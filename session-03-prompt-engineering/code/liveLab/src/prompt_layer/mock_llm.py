"""An offline, instruction-following model, so the prompt layer runs with no API key.

The Session 2 model layer returns plain sentences. Session 3 needs a model that follows
an instruction to return structured output, so this module simulates one: given a
question and the retrieved passages, it produces the fields of an ``Answer``, either as a
JSON string (Path A, prompt-for-JSON) or as typed arguments (Path B, function-calling).

It is deterministic and readable, not a real model. The ``policy`` argument stands in for
the system prompt: ``strict`` keeps it on scope and escalates what it must not answer;
``loose`` lets it guess at an out-of-scope question, which is the behaviour a good system
prompt prevents. A real or on-prem model plugs in at the same two seams in ``prompt.py``
and ``function_call.py``; nothing downstream changes.
"""

from __future__ import annotations

import json


def classify(question: str) -> str:
    """Return the coarse topic of a question: order, return, warranty, or out_of_scope."""
    q = question.lower()
    if "warrant" in q:
        return "warranty"
    if "return" in q or "refund" in q or "exchange" in q:
        return "return"
    if "order" in q or "track" in q or "deliver" in q or "cancel" in q or "arriv" in q:
        return "order"
    return "out_of_scope"


def draft(question: str, passages: list[dict], policy: str = "strict") -> dict:
    """Produce the fields of an ``Answer`` for the question, grounded in the passages.

    Answerable topics (order, return) are answered from the top retrieved passage and cite
    it. Warranty always escalates: it is legally sensitive and routes to a human. An
    out-of-scope question escalates under the strict policy, but is guessed at under the
    loose one (a non-grounded answer, which the validator and the output guardrail then
    reject).
    """
    topic = classify(question)
    citations = [p["doc_id"] for p in passages]

    if topic in ("order", "return") and citations:
        return {
            "answer": passages[0]["body"],
            "citations": citations,
            "confidence": "high",
            "escalate": False,
            "reason": f"answered from {citations[0]}",
        }
    if topic == "warranty":
        if policy == "loose":
            # The dangerous case: a weak prompt answers a sensitive warranty question
            # directly, and cites a passage, so it passes the schema. Only the output
            # policy catches it. This is exactly why the guardrail is not optional.
            return {
                "answer": "Yes, most products carry a one-year warranty, so you are covered.",
                "citations": citations or ["HC-005"],
                "confidence": "high",
                "escalate": False,
                "reason": "answered the warranty question directly (loose policy)",
            }
        return {
            "answer": "This is a warranty question. A Sunrise support agent will confirm your warranty status.",
            "citations": [],
            "confidence": "low",
            "escalate": True,
            "reason": "warranty is legally sensitive and always routes to a human",
        }
    if policy == "loose" and topic == "out_of_scope":
        return {
            "answer": "I think that should be fine.",
            "citations": [],
            "confidence": "low",
            "escalate": False,
            "reason": "guessed without grounding (loose policy)",
        }
    # Out of scope under the strict policy, or answerable but nothing was retrieved.
    return {
        "answer": "I cannot answer that from Sunrise help content. I will pass you to a support agent.",
        "citations": [],
        "confidence": "low",
        "escalate": True,
        "reason": "out of scope or not covered by the help content",
    }


def complete_json(question: str, passages: list[dict], policy: str = "strict") -> str:
    """Path A: simulate a model told to reply with JSON. Returns a JSON string to parse."""
    return json.dumps(draft(question, passages, policy))


def complete_toolcall(question: str, passages: list[dict], policy: str = "strict") -> dict:
    """Path B: simulate function-calling. Returns typed arguments a provider would have
    validated against the schema, ready to become an ``Answer``."""
    return draft(question, passages, policy)
