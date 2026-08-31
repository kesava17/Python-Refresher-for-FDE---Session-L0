# Assignment 2: add a new model adapter behind the interface

Full brief and rubric: `assignment-02.md` and `solution-02.md` (in the content repo).

The model layer defines one small interface (`generate`, `embed`) with a deterministic
offline mock as the default and a `make_model()` factory that reads `LLM_MODEL`. Your
job: add a new adapter behind the SAME interface and select it by name, without changing
any caller.

The target is a failing test. Make it pass:

```bash
poetry install
poetry run pytest          # tests/test_new_adapter.py fails until you add the adapter
```

Add an `EchoModel` whose `generate(prompt)` returns `"echo: " + prompt`, wire it into
`make_model()` so `LLM_MODEL=echo` (or `make_model("echo")`) selects it, and confirm the
default is still the offline mock. Keep secrets in the environment, never in the code.

Deliverable: the new adapter, the one-line factory change, and the passing test.
