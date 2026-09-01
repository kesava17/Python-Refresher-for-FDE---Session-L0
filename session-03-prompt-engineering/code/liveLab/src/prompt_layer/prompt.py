"""Path A: prompt-for-JSON. Ask the model for JSON, parse it, validate to ``Answer``.

The dependable, portable path: it works with any model, offline included. We assemble the
context, ask the model to reply with one JSON object, parse the reply, and validate it
against the ``Answer`` contract. If the reply is not valid JSON, or it fails validation,
we do not guess: we return the safe escalation. Failing closed is the whole point.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from prompt_layer import mock_llm
from prompt_layer.context import build_context, load_system_prompt
from prompt_layer.schema import Answer, safe_escalation


def _parse_and_validate(raw: str) -> Answer:
    """Parse a model's JSON reply and validate it to ``Answer``; escalate on any failure."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return safe_escalation("model did not return valid JSON")
    try:
        return Answer.model_validate(data)
    except ValidationError:
        return safe_escalation("model output failed schema validation")


def answer_via_prompt(
    question: str,
    passages: list[dict],
    version: str = "v2",
    model=None,
) -> Answer:
    """Answer one question through the prompt-for-JSON path.

    Offline (the default), an instruction-following mock returns the JSON. With a real
    model passed in, we send it the assembled context and parse whatever it returns. Both
    end at the same validated ``Answer``.
    """
    system_text = load_system_prompt(version)
    prompt_text, included = build_context(question, passages, system_text)
    policy = "loose" if version == "v1" else "strict"

    if model is not None:
        raw = model.generate(prompt_text)  # real seam: a live model replies with JSON
    else:
        raw = mock_llm.complete_json(question, included, policy)  # offline stand-in

    return _parse_and_validate(raw)
