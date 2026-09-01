# Prompt engineering: demos

Eight short, offline demos that make the Session 3 concepts visible. No API key, no
network: a deterministic mock (`promptlib.py`) stands in for an instruction-following
model. The one real dependency this session adds is `pydantic`, the tool teams actually
use to turn free text into a validated object.

```bash
poetry install
poetry run python freeform_vs_schema.py "How do I return an item?"
```

See `cookbook.md` for the full guided walkthrough of all eight (`prompt_parts.py`,
`context_build.py`, `alignment.py`, `freeform_vs_schema.py`, `function_call.py`,
`injection.py`, `validate.py`, `ab_prompts.py`), with what to run, what to watch for,
and what to explore.

See `demo_prompts.md` for a prompt playground: the actual prompts behind the demos, to
read, copy, and change, offline with the mock or against a real model. Start there if you
want to feel how each part of a prompt shifts the answer.

These demos need only the standard library and `pydantic`, so `python <name>.py` also
works once `pydantic` is installed. The mock is intentionally simple; its job is the
concept, not accuracy. The real model plugs in behind the same shapes in the live lab.
