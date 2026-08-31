# Solution 02 · Add a new model adapter behind the interface, without changing the caller

> The worked solution for Assignment 02. Try the assignment yourself first. This is here to check your
> work, or to unstick you when you are truly stuck. The heart of the assignment is small: one new class,
> one factory branch, one test. What matters is that they honour the seam the model layer created.

You start from the model layer you built in the live lab: the interface (`generate(prompt: str) -> str`
and `embed(texts: list[str]) -> list[list[float]]`), the deterministic offline `MockModel`, the
`make_model()` factory that reads `LLM_MODEL`, and the comparison harness that runs several models over
the golden question set. This solution adds a model behind that interface, wires it in with one line, and
proves the harness and callers run unchanged. Everything stays offline and secret-free. Use `poetry run`
for everything.

## The rubric

Grade your work against these five checks. A solution passes only if all five hold.

1. **The adapter honours the interface exactly.** It exposes `generate(self, prompt: str) -> str` and
   `embed(self, texts: list[str]) -> list[list[float]]`, returning the same types and shapes as
   `MockModel` (a string answer; one vector per input text). A caller holding it cannot tell which model
   it is. If any caller has to branch on the model type, the interface is leaking and the check fails.
2. **The factory selects it by environment variable.** `make_model()` returns the new model when
   `LLM_MODEL=<name>` is set, added as one clean branch. The environment is read inside the factory at
   call time, not at import, so a test can set the variable per case. The factory is still the only place
   that knows model names.
3. **No caller changed.** The comparison harness, the `mock_model` demo, and every other caller run
   against the new model with no edit. The offline `MockModel` stays the default when `LLM_MODEL` is
   unset, so the existing tests and demos run exactly as before.
4. **No secret in the repo.** No key, endpoint, or token appears in any committed file. A provider-shaped
   stub reads its key from an environment variable at call time and raises a clear error when it is
   missing, so a misconfigured deployment fails loudly rather than silently sending a blank credential.
5. **A test proves it.** One test selects the new model through the factory and runs the harness (or a
   caller) over the golden questions, asserting output for every model and no exception, and confirms the
   unset-default returns `MockModel`. The existing model-layer tests pass with no change.

The point behind all five is one idea: the code above the interface depends on the interface, not on any
model. Adding a model is a local change; nothing upstream moves.

## Reference sketch: a clean adapter

Two shapes both pass. The first keeps the whole assignment offline; the second shows the discipline for a
real provider. Prefer the offline mock as your graded deliverable, because it lets the harness actually
run your model with no network.

### Shape A: a second offline mock (recommended)

A second deterministic model with its own behaviour, so a comparison has something to compare. Here it
answers more cautiously than the default mock, escalating any query it is not confident about, which fits
the Sunrise warranty guardrail. It reuses the layer's embedding helper so the vectors stay in the same
shape.

**`model_layer/model.py`** (the new adapter, beside `MockModel`)

```python
class CautiousMockModel:
    """A second offline model behind the same interface, tuned to escalate sooner.

    It answers the confident cases directly and hands anything else to a human, which
    is the conservative posture the warranty category wants. It is deterministic and
    dependency-free, so tests stay stable and everything runs with no key and no network.
    """

    ESCALATION = (
        "I am not fully sure about this one, so a human agent will take it from here."
    )

    def generate(self, prompt: str) -> str:
        p = prompt.lower()
        if "return" in p or "refund" in p:
            return "To return an item, open My Orders, pick the item, and choose Return."
        if "where" in p and "order" in p:
            return "Track your order in My Orders using the tracking link or the order id."
        # Anything else, including every warranty question, is escalated, not guessed.
        return self.ESCALATION

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Reuse the layer's deterministic embedding so the vector shape matches MockModel:
        # one vector per input text, same dimension.
        return [_embed_one(t) for t in texts]
```

The class says nothing a caller must know beyond the two methods. `generate` returns a `str`, `embed`
returns one vector per input text, exactly the shapes `MockModel` returns. That sameness is the whole
job: a caller cannot tell the two models apart through the interface, which is why no caller has to
change.

### Shape B: a real or on-prem stub (the secret discipline)

When the model is a real provider, the adapter reads its secret from the environment at call time and
never from a file. For an offline assignment it need not make a live call; what matters is the shape.

**`model_layer/model.py`** (the provider-shaped adapter)

```python
import os


class OnPremModel:
    """Adapter for an on-prem or hosted model. The key and endpoint come from the
    environment at call time, never from a committed file, so no secret lives in the repo."""

    def __init__(self) -> None:
        # Read config at construction, but do not fail here: a test can build the object
        # offline. The key is checked at call time, where it is actually needed.
        self._endpoint = os.environ.get("LLM_ENDPOINT", "")

    def _key(self) -> str:
        key = os.environ.get("LLM_API_KEY")
        if not key:
            # Fail loudly: a missing key is a deployment error, not a blank credential to
            # send on the wire.
            raise RuntimeError("LLM_API_KEY is not set; cannot call the on-prem model")
        return key

    def generate(self, prompt: str) -> str:
        key = self._key()  # read the secret from the environment, at the moment of use
        # A real adapter would POST prompt to self._endpoint with this key and return the
        # answer. Offline, we keep the shape and return a deterministic stand-in.
        return f"[on-prem answer for: {prompt[:40]}]"

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._key()
        return [_embed_one(t) for t in texts]
```

The secret is read with `os.environ.get("LLM_API_KEY")` inside `_key()`, at the moment of use, and a
missing key raises a clear error. No key literal appears anywhere. This is the pattern every real
provider adapter follows.

## The one-line factory change

`make_model()` gains one branch. Nothing else moves.

**`model_layer/model.py`** (the factory)

```python
def make_model(name: str | None = None) -> Model:
    """Return the model named by LLM_MODEL, defaulting to the offline mock.

    The environment is read here, at call time, so switching models is a deployment
    setting and not a code change. This factory is the only place that knows model names.
    """
    name = name or os.environ.get("LLM_MODEL", "mock")
    if name == "mock":
        return MockModel()
    if name == "cautious":          # <- the one new branch
        return CautiousMockModel()
    raise ValueError(f"unknown model: {name!r}")
```

With `LLM_MODEL` unset, `name` falls back to `"mock"` and the default offline model is returned, so every
existing caller and test runs unchanged. Set `LLM_MODEL=cautious` and the same `make_model()` call hands
back the new model instead. The callers never learn a new name; the factory carries that knowledge alone.

`Model` here is the interface the layer declares (a `typing.Protocol` with `generate` and `embed`, or a
small base class). Your new adapter satisfies it by having the two methods, so no registration beyond the
factory branch is needed.

## The test (the deliverable proof)

One test file proves the seam holds: the new model is reachable through the factory, the harness runs it
over the golden questions, and the default is still the offline mock.

**`tests/test_model_layer.py`** (the new tests)

```python
import os

from model_layer.model import CautiousMockModel, MockModel, make_model
from model_layer.harness import compare_models, GOLDEN_QUESTIONS


def test_factory_selects_new_model_by_env(monkeypatch) -> None:
    # LLM_MODEL selects the new adapter through the same factory the callers use.
    monkeypatch.setenv("LLM_MODEL", "cautious")
    model = make_model()
    assert isinstance(model, CautiousMockModel)


def test_default_stays_the_offline_mock(monkeypatch) -> None:
    # With nothing set, the deterministic offline mock is still the default.
    monkeypatch.delenv("LLM_MODEL", raising=False)
    assert isinstance(make_model(), MockModel)


def test_harness_runs_unchanged_with_the_new_model() -> None:
    # The caller does not change: the same harness runs both models over the golden
    # questions and produces a non-empty answer for every one, with no exception.
    results = compare_models(["mock", "cautious"], GOLDEN_QUESTIONS)
    for name in ("mock", "cautious"):
        answers = results[name]
        assert len(answers) == len(GOLDEN_QUESTIONS)
        assert all(a.strip() for a in answers)
```

`test_factory_selects_new_model_by_env` proves the wire: `LLM_MODEL=cautious` returns the new model from
`make_model()`. `test_default_stays_the_offline_mock` proves the default is untouched. And
`test_harness_runs_unchanged_with_the_new_model` is the payoff: the harness, which you did not edit, runs
both models and returns an answer for every golden question. `monkeypatch.setenv` sets the environment
per test, so cases do not leak into each other, and no secret is ever written down.

If you built the provider stub, add one more test that sets a dummy `LLM_API_KEY`, builds the model, and
asserts a clear error when the key is removed, with no key literal in the test:

```python
def test_onprem_reads_key_from_env_and_fails_loudly_without_it(monkeypatch) -> None:
    from model_layer.model import OnPremModel

    monkeypatch.setenv("LLM_API_KEY", "dummy-value-for-the-test")
    OnPremModel().generate("hello")  # a set key is enough; no literal key in the repo

    monkeypatch.delenv("LLM_API_KEY", raising=False)
    import pytest
    with pytest.raises(RuntimeError):
        OnPremModel().generate("hello")
```

## Green gate and commit

```bash
poetry run pytest -q          # existing model-layer tests plus the new ones, all green
poetry run ruff check .       # All checks passed!
poetry run mypy .             # Success: no issues found
git add .
git commit -m "model layer: add a second adapter behind the interface, selected by LLM_MODEL"
```

Run the harness both ways while you are here, to see the seam with your own eyes:

```bash
poetry run python -m model_layer.harness              # default mock in the table
LLM_MODEL=cautious poetry run python -m model_layer.harness   # the new model in the table
```

The demo runs the same way against the new model with no edit to the demo file:

```bash
LLM_MODEL=cautious poetry run python mock_model.py
```

## Done when

- The new adapter exposes `generate(self, prompt: str) -> str` and `embed(self, texts: list[str]) ->
  list[list[float]]`, in the same shapes as `MockModel`, and nothing else a caller must special-case.
- `make_model()` returns the new model when `LLM_MODEL=<name>` is set, added as one clean branch, with
  the environment read at call time.
- With `LLM_MODEL` unset, `make_model()` still returns the deterministic offline `MockModel`.
- The comparison harness and the `mock_model` demo run against the new model with no edit to any caller.
- No key, endpoint, or token appears in any committed file; a provider stub reads its key from the
  environment at call time and fails loudly when it is missing.
- A test selects the new model through the factory, runs the harness or a caller over the golden
  questions with output for every model and no exception, and confirms the unset-default returns
  `MockModel`.
- The existing model-layer tests pass with no change, and ruff and mypy are clean, and the layer is
  committed.

You have proven the model layer's promise. A new model went in behind the interface, an environment
variable selected it, the harness and the callers ran unchanged, and no secret reached the repo. This is
the seam every later session leans on: the day Sunrise moves the bot from the offline mock to an on-prem
model, the change is one setting, not a rewrite. Programming to an interface is what makes that true, and
you have just built the proof.
