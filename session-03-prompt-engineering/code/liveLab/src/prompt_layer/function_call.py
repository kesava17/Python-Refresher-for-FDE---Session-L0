"""Path B: function-calling / tool-use. The model returns typed arguments, not a string.

The modern native way to get structure: the model calls a tool whose arguments the
provider validates against a schema, so you receive typed fields instead of a JSON string
to parse. It needs a real model, so this builds the seam plus an offline mock that
simulates the tool call, and validates the result against the SAME ``Answer`` contract as
Path A. Both paths land on the same object, so nothing downstream cares which was used.
"""

from __future__ import annotations

from pydantic import ValidationError

from prompt_layer import mock_llm
from prompt_layer.schema import Answer, safe_escalation

# The tool schema we would register with a real provider: the model is told to call this
# tool, and its arguments must match the Answer schema.
TOOL_SCHEMA = {
    "name": "return_answer",
    "description": "Return the support answer in the required structure.",
    "parameters": Answer.model_json_schema(),
}


def answer_via_toolcall(
    question: str,
    passages: list[dict],
    version: str = "v2",
    model=None,
) -> Answer:
    """Answer one question through the function-calling path.

    Offline, a mock returns the typed arguments. A real tool-calling model plugs in at the
    same seam and returns the same argument shape. Either way we validate to ``Answer`` and
    fail closed if the arguments do not fit.
    """
    policy = "loose" if version == "v1" else "strict"

    if model is not None:
        # Real seam: call the model with TOOL_SCHEMA registered and read the tool arguments.
        raise NotImplementedError(
            "Wire your provider's tool-calling API here, passing TOOL_SCHEMA and reading "
            "the returned arguments. Offline, leave model=None to use the mock."
        )
    tool_args = mock_llm.complete_toolcall(question, passages, policy)

    try:
        return Answer.model_validate(tool_args)
    except ValidationError:
        return safe_escalation("tool-call arguments failed schema validation")
