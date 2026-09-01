# Solution 01 · Repair a flaky prompt, and add a validated field

> The worked solution for Assignment 01. Try the assignment yourself first. This is here to
> check your work, or to unstick you. There is a correct method: fix the output at the prompt,
> grow the contract by one typed field, and keep every guarantee. This solution shows the two
> small changes and the reasoning that makes them the right ones.

The assignment is not about these two lines of code; it is about a habit. When output is
wrong "sometimes", you do not sprinkle special cases through the caller. You let the schema
name the failing case, fix it at the source, and, when the contract needs to say more, add a
field that is validated like every other. Below is the reference fix and the rubric to grade
your own against.

## What a strong repair shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Fixed at the prompt** | The flaky answer is repaired where it was produced (the draft attaches its citation), not by editing the caller or the test. |
| **Did not weaken the rule** | The `citations`-when-not-escalating rule is untouched. The bug was fixed by meeting the rule, not by removing it. |
| **No dishonest escape** | `escalate` was not flipped to dodge the rule, and no citation that was never retrieved was invented. The answer is genuinely grounded, so it genuinely cites. |
| **Field is validated** | `topic` is a `Literal` over the allowed set, so an invalid value cannot be constructed, exactly like `confidence`. A plain `str` field would earn no mark. |
| **One source of truth** | `topic` is set from the classifier the draft already ran, not classified a second time in the schema or the caller. |
| **Proven still strict** | A small added test shows an uncited non-escalated answer and an invalid topic both still raise. |

The trap this assignment exists to catch is the tempting "quick fix": making the red test
green by loosening the validator (dropping the citation rule) or by lying (`escalate=True` on
an answer that is not really an escalation). Both make the test pass and the assistant worse.
The discipline is to fix the real defect and leave the guardrail standing.

## The reference fix

Two small changes.

**1. Repair the return prompt** in `mock_llm.py`: pass the citation through, the way order
already does.

```python
if topic == "return":
    doc_id, body = _DOC["return"]
    return {"answer": body, "citations": [doc_id], "topic": "return",
            "confidence": "high", "escalate": False,
            "reason": "answered from return help content"}
```

**2. Add the `topic` field** to `Answer` in `schema.py`, typed like `confidence`:

```python
class Answer(BaseModel):
    answer: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    reason: str = Field(min_length=1)
    topic: Literal["order", "return", "warranty", "out_of_scope"]
```

Then set `topic` on every returned draft (order, return, warranty, out_of_scope) from the
classifier the draft already computed. Run the tests:

```bash
poetry run pytest
# 2 passed
```

## Why this is the right shape

The citation rule is what made the flaky prompt fail in a test instead of in front of a
customer. Removing it to "fix" the test would trade a loud, cheap failure for a silent,
expensive one: an answer with no source, shown as fact. Fixing the draft keeps the rule and
removes the defect.

Adding `topic` as a `Literal` rather than a `str` is the same principle applied to growth. A
string field would accept `"orders"`, `"warrantee"`, or `""`, and the bug would surface
downstream, in a report or a routing rule, far from its cause. A `Literal` moves that failure
to the moment of construction, where it is a one-line fix. Every field you add to a contract
is a chance to either add a guarantee or add a liability; validated-by-default is how you keep
choosing the first.

## Going further (optional)

- Add a rule that `topic == "warranty"` implies `escalate is True`, as a model validator, so
  the sensitive-topic policy is expressed in the contract itself, not only in the guardrail.
- Add a `topic` breakdown to a small report over the held set (how many answers per topic,
  how many escalated), the seed of the telemetry you build in Session 5.
