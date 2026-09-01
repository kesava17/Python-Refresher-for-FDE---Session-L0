"""The prompt layer behind one call: ``answer(question) -> Answer``.

This ties the session together in the order the concepts were taught: the input guardrail
runs first (untrusted input, fail closed on injection), then the right context is
retrieved and assembled, then the model produces a structured answer by either path, and
finally the output policy enforces the escalation rules. The result is always a valid,
trustworthy ``Answer`` the rest of the assistant can act on. Session 5 assembles this with
the grounding layer into the full PoC.
"""

from __future__ import annotations

from model_layer.corpus import load_corpus
from prompt_layer.context import retrieve
from prompt_layer.function_call import answer_via_toolcall
from prompt_layer.guardrails import apply_output_policy, check_input
from prompt_layer.prompt import answer_via_prompt
from prompt_layer.schema import Answer, safe_escalation


def answer(question: str, path: str = "a", version: str = "v2", model=None) -> Answer:
    """Answer one support question, guarded end to end.

    ``path`` selects the structured-output route: ``"a"`` for prompt-for-JSON, ``"b"`` for
    function-calling. Both return the same validated ``Answer``. ``version`` selects the
    system prompt variant, and ``model`` plugs in a real model in place of the offline mock.
    """
    # 1. Input guardrail: reject an injection attempt before the model ever runs.
    injection_reason = check_input(question)
    if injection_reason:
        return safe_escalation(injection_reason)

    # 2. Context engineering: retrieve the passages that matter for this question.
    passages = retrieve(question, load_corpus())

    # 3. Structured output: produce a validated Answer by the chosen path.
    if path == "b":
        draft = answer_via_toolcall(question, passages, version, model)
    else:
        draft = answer_via_prompt(question, passages, version, model)

    # 4. Output guardrail: enforce the escalation policy whatever the model returned.
    return apply_output_policy(draft, question)
