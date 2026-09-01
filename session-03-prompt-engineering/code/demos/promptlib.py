"""Offline stand-ins for an instruction-following model, so the Session 3 demos run
with no API key.

Deterministic and dependency-light: the standard library plus pydantic, the one real
tool we add this session. This is NOT a real model. It is just enough behaviour to make
the ideas visible: the parts of a prompt, a context with a token budget, structured
output two ways, a guardrail, and a validator. The point of the demos is the concept.

Everything a real model would decide is faked with a small, readable rule set, so the
same input always gives the same output and you can reason about why.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# The structured contract every later layer honours.
# ---------------------------------------------------------------------------
class Answer(BaseModel):
    """The one output shape the whole assistant agrees on.

    pydantic is the schema and the validator in one: a wrong type, a bad
    ``confidence`` value, or a missing field raises here, before any caller trusts the
    result. The extra rule (a grounded answer must cite a source) is expressed as a
    model validator, so the object cannot exist in an invalid state.
    """

    answer: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def _grounded_answers_must_cite(self) -> "Answer":
        """A non-escalated answer must cite at least one source; an escalation need not."""
        if not self.escalate and not self.citations:
            raise ValueError("a non-escalated answer must include at least one citation")
        return self


# ---------------------------------------------------------------------------
# A tiny help corpus, so grounded demos have a real source to cite.
# ---------------------------------------------------------------------------
CORPUS: list[dict] = [
    {"doc_id": "HC-001", "topic": "order",
     "body": "Track your order in My Orders using the tracking link or the order id."},
    {"doc_id": "HC-003", "topic": "return",
     "body": "Start a return from My Orders; a prepaid label is emailed to you."},
    {"doc_id": "HC-005", "topic": "warranty",
     "body": "Warranty claims are assessed by a Sunrise support agent, not by the bot."},
]

_ANSWER_TEXT = {
    "order": "Track your order in My Orders using the tracking link or the order id.",
    "return": "Open My Orders, choose the item, and select Return. A prepaid label is emailed to you.",
}


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


def retrieve(question: str, corpus: list[dict] | None = None) -> list[dict]:
    """Return the corpus passages whose topic matches the question (a stand-in for the
    real retrieval built in Session 4)."""
    topic = classify(question)
    return [d for d in (corpus or CORPUS) if d["topic"] == topic]


def estimate_tokens(text: str) -> int:
    """Approximate a token count: words and punctuation marks. Real tokenizers differ,
    but this is close enough to reason about a context budget."""
    return max(1, len(re.findall(r"\w+|[^\w\s]", text)))


def draft(question: str, passages: list[dict], policy: str = "strict") -> dict:
    """Simulate what an instruction-following model would return for the assembled prompt.

    The ``policy`` argument stands in for the system prompt: ``strict`` keeps the model on
    scope and escalates what it should not answer, while ``loose`` lets it guess at an
    out-of-scope question (which is exactly the behaviour we do not want). Returns a plain
    dict so the two structured-output paths can each build an ``Answer`` from it.
    """
    topic = classify(question)
    citations = [p["doc_id"] for p in passages]
    if topic in ("order", "return"):
        return {
            "answer": _ANSWER_TEXT[topic],
            "citations": citations,
            "confidence": "high" if citations else "medium",
            "escalate": False,
            "reason": f"answered from {topic} help content",
        }
    if topic == "warranty":
        if policy == "loose":
            # A weak prompt answers a sensitive warranty question directly instead of
            # handing it to a human. It even cites a source, so the schema lets it pass:
            # only a policy guardrail catches this one.
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
    # out of scope
    if policy == "loose":
        return {
            "answer": "I think that should be fine.",
            "citations": [],
            "confidence": "low",
            "escalate": False,
            "reason": "guessed without grounding (loose policy)",
        }
    return {
        "answer": "I cannot answer that from Sunrise help content. I will pass you to a support agent.",
        "citations": [],
        "confidence": "low",
        "escalate": True,
        "reason": "out of scope for the help content",
    }


def complete_json(question: str, passages: list[dict], policy: str = "strict") -> str:
    """Path A: simulate a model told to reply with JSON. Returns a JSON string to parse."""
    import json
    return json.dumps(draft(question, passages, policy))


def complete_toolcall(question: str, passages: list[dict], policy: str = "strict") -> dict:
    """Path B: simulate function-calling. Returns typed arguments the provider would have
    validated against a schema, as a dict ready to become an ``Answer``."""
    return draft(question, passages, policy)


# ---------------------------------------------------------------------------
# A small input guardrail: catch the obvious prompt-injection attempts.
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS = [
    "ignore your rules",
    "ignore previous",
    "ignore all instructions",
    "disregard",
    "forget your instructions",
    "reveal the system prompt",
    "show me your system prompt",
    "what is your system prompt",
]


def looks_like_injection(text: str) -> bool:
    """Return True when the input tries to override the assistant's instructions."""
    low = text.lower()
    return any(pattern in low for pattern in _INJECTION_PATTERNS)
