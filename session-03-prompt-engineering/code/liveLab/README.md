# Prompt and output layer (live lab)

The second layer of the Sunrise Support Deflection Assistant, built on Session 2's model
layer. It turns a free-text model into a component the rest of the assistant can trust: a
`pydantic`-validated `Answer` produced two ways, engineered context within a token budget,
an aligned system prompt, and input and output guardrails that escalate rather than guess.

```bash
poetry install
poetry run python -m prompt_layer.evaluate   # score the prompt versions on the held set
poetry run pytest                             # run the tests
```

## What is here

```
src/model_layer/          carried forward from Session 2 (the pluggable model, the corpus)
src/prompt_layer/
  schema.py               the pydantic Answer contract + safe_escalation (the safe exit)
  mock_llm.py             an offline instruction-following model (returns JSON or tool args)
  context.py              retrieval stub, token budget, and context assembly
  prompt.py               Path A: prompt-for-JSON, parsed and validated to Answer
  function_call.py        Path B: function-calling (mock + real seam), same Answer
  guardrails.py           input guard (injection) + output policy (escalation rules)
  answerer.py             the whole layer behind one call: answer(question) -> Answer
  evaluate.py             test a prompt like code: score v1 vs v2 on the held set
  prompts/                versioned system prompts (system_v1.txt weak, system_v2.txt strict)
data/
  help_corpus.json        the shared Sunrise help articles (from Session 2)
  golden_questions.csv    the shared golden set (from Session 2)
  prompt_tests.csv        the held test set for this session (14 labelled questions)
tests/                    schema, context, guardrails, and end-to-end answerer tests
```

## The Answer contract

Every answer is one validated object:

```
answer: str
citations: list[str]
confidence: "high" | "medium" | "low"
escalate: bool
reason: str
```

`escalate` is where warranty and out-of-scope questions route to a human; `reason` is the
seed of the compliance audit trail. Two ways produce it, both landing on the same object:

- **Path A, prompt-for-JSON** (`prompt.py`): ask the model for JSON, parse, validate.
  Portable and offline.
- **Path B, function-calling** (`function_call.py`): the model returns typed arguments the
  provider validates. A real-model seam plus an offline mock.

## Defence in depth

Three checks, not one. The **schema** rejects malformed output (an uncited answer). The
**output policy** enforces the business rules (warranty and out-of-scope always escalate,
low confidence escalates). The **input guardrail** catches injection before the model
runs. `evaluate.py` shows why the prompt still matters: the weak v1 prompt answers a
warranty question directly, and although the guardrail rescues it at runtime, you ship the
better prompt anyway.

## Offline by default, real when you want

The mock runs with no API key. A real or on-prem model plugs in at the seams in `prompt.py`
and `function_call.py`, selected through the Session 2 model layer (`LLM_MODEL`), with the
key read from the environment and never written in the repo.
