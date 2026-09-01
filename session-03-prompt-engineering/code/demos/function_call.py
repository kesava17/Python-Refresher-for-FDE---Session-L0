"""Demo 5: structured output the modern native way, function-calling / tool-use.

Path A asks the model to write JSON and we parse it. Path B, function-calling, has the
model return typed arguments directly, which the provider validates against a schema
before they reach us. It needs a real model, so here an offline mock returns the typed
arguments and we validate them to the SAME ``Answer`` contract. Both paths end at the
same object, so the rest of the assistant does not care which was used.

Run:  poetry run python function_call.py "Is my product under warranty?"
"""

from __future__ import annotations

import sys

from promptlib import Answer, complete_toolcall, retrieve


# The tool schema we would register with a real provider. The model is told to call this
# tool with arguments in this shape, and the provider checks them for us.
TOOL_SCHEMA = {
    "name": "return_answer",
    "description": "Return the support answer in the required structure.",
    "parameters": Answer.model_json_schema(),
}


def main() -> None:
    """Show a mock tool call, then validate its typed arguments to the Answer contract."""
    question = sys.argv[1] if len(sys.argv) > 1 else "Is my product under warranty?"
    passages = retrieve(question)

    print(f'question: "{question}"\n')
    print(f"registered tool: {TOOL_SCHEMA['name']}  (arguments must match the Answer schema)\n")

    # The model returns typed arguments (a dict), not a string to parse.
    tool_args = complete_toolcall(question, passages)
    print("TOOL CALL (typed arguments the model returned):")
    print(f"    {tool_args}\n")

    # Same validation, same contract: build the Answer and the rest of the code is identical.
    answer = Answer.model_validate(tool_args)
    print("VALIDATED Answer (identical shape to Path A):")
    print(f"    {answer.model_dump()}")
    print(f"    escalate={answer.escalate}  ->  {'hand off to a human' if answer.escalate else 'answer the user'}")
    print()
    print("Path A (prompt-for-JSON) is portable and works offline. Path B (function-")
    print("calling) is native and the provider validates for you. Both land on one Answer.")


if __name__ == "__main__":
    main()
