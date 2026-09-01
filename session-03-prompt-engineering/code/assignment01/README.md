# Assignment 1: repair a flaky prompt, and add a validated field

Full brief and rubric: `assignment-01.md` and `solution-01.md` (in the content repo).

The prompt layer returns an `Answer` that a validator checks before any caller trusts it.
This starter has a **flaky prompt**: the return-topic answer forgets its citation, so a
confident, non-escalated answer arrives with no source and fails the validator. It also
does not tag answers with a `topic` yet.

Two target tests fail. Make them pass:

```bash
poetry install
poetry run pytest          # tests/test_repair.py has two failing tests
```

1. **Repair the flaky prompt** so every held question produces a valid `Answer` (attach
   the return citation in `mock_llm.draft`, the same way the order topic already does).
2. **Add a `topic` field** to the `Answer` schema, validated against the allowed list
   (`order`, `return`, `warranty`, `out_of_scope`) with `Literal[...]`, and set it in the
   draft, so every answer is tagged with its topic.

Deliverable: the repaired prompt, the new validated field, and both tests green.
