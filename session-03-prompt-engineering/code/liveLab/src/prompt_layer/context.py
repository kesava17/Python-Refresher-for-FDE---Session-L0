"""Context engineering: assemble what the model sees, within a token budget.

Context is more than the instruction. This module retrieves the passages that matter,
orders them (rules first, sources next), and fits them into a budget that always leaves
room for the answer. The retriever here is a simple keyword ranker, a deliberate stand-in
for the real embedding retrieval built in Session 4; the point now is the assembly and
the budget, not the search quality.
"""

from __future__ import annotations

import os
import re

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# A generous default budget for the whole prompt, in approximate tokens. Large enough to
# hold the strict system prompt, a few-shot example, and the top retrieved passages.
DEFAULT_BUDGET = 400
ANSWER_ROOM = 40  # tokens kept free for the model's reply


def load_system_prompt(version: str = "v2") -> str:
    """Load a versioned system prompt from the prompts folder (for example v1 or v2)."""
    path = os.path.join(_PROMPTS_DIR, f"system_{version}.txt")
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip()


def estimate_tokens(text: str) -> int:
    """Approximate a token count: words and punctuation marks. Close enough to budget."""
    return max(1, len(re.findall(r"\w+|[^\w\s]", text)))


def retrieve(question: str, corpus: list[dict], k: int = 2) -> list[dict]:
    """Return the top-k passages by keyword overlap with the question (a Session 4 stub).

    A crude ranker: score each passage by how many of the question's words appear in its
    title and body, and keep the best few. Real semantic retrieval replaces this in
    Session 4; the interface (question in, ranked passages out) stays the same.
    """
    q_words = set(re.findall(r"[a-z]{3,}", question.lower()))
    scored: list[tuple[int, dict]] = []
    for doc in corpus:
        text = f"{doc.get('title', '')} {doc.get('body', '')}".lower()
        overlap = sum(1 for w in q_words if w in text)
        if overlap:
            scored.append((overlap, doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:k]]


def build_context(
    question: str,
    passages: list[dict],
    system_text: str,
    budget: int = DEFAULT_BUDGET,
    few_shot: bool = True,
) -> tuple[str, list[dict]]:
    """Assemble the prompt within the budget and return it with the passages that fit.

    Order: the system prompt (the rules), an optional few-shot example (the shape of a
    good answer), the retrieved passages (the sources), then the question. Passages that
    would break the budget are dropped, and the ones that made it are returned so the
    model is only asked to cite what it was actually shown.
    """
    lines = [system_text]
    used = estimate_tokens(system_text)

    if few_shot:
        example = ('Example -> Q: "How do I return an item?"  '
                   'A: answer from the return passage and cite its id; do not guess.')
        lines += ["", example]
        used += estimate_tokens(example)

    lines += ["", "Context:"]
    included: list[dict] = []
    for doc in passages:
        entry = f"[{doc['doc_id']}] {doc['body']}"
        cost = estimate_tokens(entry)
        if used + cost > budget - ANSWER_ROOM:
            continue  # over budget: drop the least relevant remaining passage
        used += cost
        included.append(doc)
        lines.append(entry)

    lines += ["", f"Q: {question}", "Return one JSON object for the Answer schema."]
    return "\n".join(lines), included
