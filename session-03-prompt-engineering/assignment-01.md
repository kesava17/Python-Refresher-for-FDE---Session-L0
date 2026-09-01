# Assignment 01 · Repair a flaky prompt, and add a validated field

> Offline practice for the prompt engineering topic. In the live lab you made the model's
> output reliable: a `pydantic` `Answer` that a validator checks before any code trusts it.
> Now you do the everyday FDE job that keeps a prompt honest: a teammate's prompt is flaky,
> and it needs one more field. You will repair the prompt so every answer validates, and add
> a new output field with its own validation rule, so the contract carries more meaning
> without losing its guarantees. Everything runs offline. No API key, no network, no cost.

This is a do-it-yourself assignment. The point is to feel why a schema is worth having: it
turns "the output looks wrong sometimes" into a test that fails on the exact case, and it
makes adding a field a small, safe change instead of a leap of faith. The starter is a
working prompt layer with two problems planted in it. Your job is to make the target tests
pass without loosening the contract.

Start from the assignment project (`code/.../session-03-prompt-engineering/assignment01`).
The two target tests fail on the starter:

```bash
cd assignment01
poetry install
poetry run pytest
```

The prompt layer is `prompt_layer`: `schema.py` holds the `Answer` contract, `mock_llm.py`
holds the offline model draft, and `answerer.py` validates the draft into an `Answer`. The
held test set is `data/prompt_tests.csv`, the same labelled questions the live lab used.

## The goal

Two target tests, both green, with the contract still strict:

1. **Every held question returns a valid `Answer`.** The starter's return-topic prompt is
   flaky: it produces a confident, non-escalated answer with no citation, which the
   validator rejects. Repair the prompt so it passes the source through.
2. **Every `Answer` carries a `topic`.** Add a new field to the schema, validated against an
   allowed list, and set it in the draft, so each answer is tagged with the topic it belongs
   to.

You do not weaken the validator to make the first test pass. A flaky prompt is fixed at the
prompt, not by removing the rule that caught it.

## Staged guidance

Work in small stages; run the tests after each.

### Level 1: see the failures, and read them

Run `poetry run pytest` and read the two failures before touching anything. One is a
`ValidationError` on a return question (the uncited, non-escalated answer). The other is an
`AttributeError` for a missing `topic`. The tests are telling you exactly what is wrong; let
them.

Hint: this is the schema doing its job. The bad answer never reached a user; it failed loudly
in a test instead. That is the whole argument for a validated contract.

### Level 2: repair the flaky prompt

Open `mock_llm.py`. The order topic attaches its citation; the return topic does not. Make
the return branch pass its `doc_id` through, the same way order does, so a grounded answer
carries the source it stood on.

Hint: do not "fix" this by setting `escalate` to true, or by adding a citation that was never
retrieved. The answer really is grounded in the return doc; the bug is that the prompt
dropped the reference. Attach the real one.

### Level 3: add the `topic` field to the contract

Open `schema.py`. Add a `topic` field to `Answer`, typed as a `Literal` over the allowed set
(`order`, `return`, `warranty`, `out_of_scope`), exactly the way `confidence` is typed. Now
an answer with a misspelled or invented topic cannot be built at all.

Hint: put the field on the model first and watch the tests change. Every draft that does not
yet set a `topic` will now fail to validate, which is precisely the signal you want: the
schema tells you every place that has to be updated.

### Level 4: set the topic in the draft

Back in `mock_llm.py`, set `topic` on each returned draft (the classifier already computes
it). Run the tests. Both should pass, and every answer now carries a validated topic a caller
can route or report on.

Hint: reuse the topic the draft already classified; do not classify twice. One source of
truth for the topic keeps the field honest.

### Level 5: prove you did not loosen the contract

Add one small test of your own: a non-escalated answer with an empty `citations` list must
still raise, and an answer with `topic="orders"` (note the trailing s) must still raise.
Confirm both. This is how you show the repair added meaning without removing a guarantee.

Hint: a repair that also quietly weakened the validator is not a repair. The extra test is
your evidence that the rules that caught the bug are all still standing.

## Done when

- [ ] Both target tests in `tests/test_repair.py` pass.
- [ ] The return-topic prompt attaches its real citation; `escalate` was not flipped and no
  fake source was invented.
- [ ] `Answer` has a `topic` field, typed as a `Literal` over the allowed list, so an invalid
  topic cannot be constructed.
- [ ] The draft sets `topic` from the classifier, once, for every branch.
- [ ] The `citations`-when-not-escalating rule and the `topic` rule both still reject bad
  input, proven by a test you added.
- [ ] Nothing in the validator was loosened to make a test pass.

When every box is ticked, you have done the everyday job that keeps a prompt trustworthy: you
fixed the output at the prompt, not by lowering the bar, and you grew the contract by one
field without giving up a single guarantee. The worked solution is in `solution-01.md` if you
want to compare, but try first.
