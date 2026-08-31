# Assignment 02 · Add a new model adapter behind the interface, without changing the caller

> Offline practice for the LLM Foundations session. In the live lab you built the model layer: one
> small interface, a deterministic offline `MockModel` behind it, a `make_model()` factory that picks a
> model from an environment variable, and a comparison harness that runs several models over the golden
> questions. Now you add a second model behind the same interface and prove the payoff: the harness and
> every caller run unchanged, and no secret ever touches the repo.

This is a do-it-yourself assignment. It has one lesson at its centre, the lesson every solution builder
needs before touching a real provider: **program to an interface, not to a model.** When the rest of
your code depends only on `generate(prompt)` and `embed(texts)`, you can swap the thing behind that
interface, from a mock to a second mock to a real or on-prem provider, and nothing upstream has to
change. The factory picks the model from the environment, so the choice is a deployment setting, not a
code edit. Secrets live in the environment too, never in a source file. You already have the layer; this
assignment makes you exercise the seam it created.

For the Sunrise Electronics bot this is not academic. Today the bot runs on the offline mock so every
build is testable with no key, no network, and no cost. Tomorrow it may run on an on-prem model in the
Sunrise data centre, and the day after on a hosted one. The interface is the promise that none of those
moves reaches the call-center logic, the harness, or the tests. You are going to make that promise real
by adding a model and watching everything above it stay still.

## The goal

Add one new model behind the existing interface and wire it in so a single environment variable selects
it. Concretely:

1. **Write a new adapter that honours the interface exactly.** A class with `generate(self, prompt: str)
   -> str` and `embed(self, texts: list[str]) -> list[list[float]]`, and nothing the callers have to
   know about beyond those two methods. It behaves differently from the default mock, so a comparison
   has something to compare, but it speaks the same interface.
2. **Wire it into the factory with a one-line change.** `make_model()` reads `LLM_MODEL`; add your model
   as one more branch so `LLM_MODEL=<name>` returns it. Setting the variable is the only thing a
   deployment does to switch models.
3. **Keep the offline mock the default.** With `LLM_MODEL` unset, `make_model()` still returns the
   deterministic `MockModel`, so every existing test and demo runs offline exactly as before.
4. **Keep every secret in the environment.** If your adapter stands in for a real or on-prem model, its
   key comes from an environment variable read at call time. No key, endpoint, or token is written in
   any file you commit.
5. **Prove it with a test.** One test selects your model through the factory and runs the comparison
   harness (or a caller) over the golden questions, and asserts it produces output for every model
   without error. The existing tests keep passing with no edit.

By the end you have shown the seam works: a new model dropped in behind the interface, chosen by an
environment variable, with the harness and callers running unchanged and not one secret in the repo.

## The starting point

You already have the model layer from the live lab. Reuse all of it:

- **The interface.** `generate(prompt: str) -> str` returns an answer; `embed(texts: list[str]) ->
  list[list[float]]` returns one vector per input text. That pair is the whole contract the rest of the
  code depends on.
- **`MockModel`.** The deterministic, dependency-free offline model. Same prompt in, same answer out,
  every run. No key, no network, no cost. This stays the default.
- **`make_model(name=None)`.** The factory. It reads `LLM_MODEL` from the environment when no name is
  passed, and returns the matching model. Today it knows one name.
- **The comparison harness.** It builds a few models, runs them over the golden question set, and prints
  a small table so you can choose a model on evidence rather than on a vendor's claim.
- **The golden question set.** The three Sunrise query types (order status, returns, warranty) plus a
  couple of edge cases, the same set the whole phase reuses.

This assignment adds a model beside the mock. It does not change the interface, the harness, the golden
set, or any caller. That last point is the deliverable: if you find yourself editing a caller to make
the new model fit, the new model is not honouring the interface, and that is the bug to fix.

## What you have to build

1. **One new adapter.** Pick one of the two shapes:
   - **A second offline mock** (recommended, because it keeps the whole assignment offline and lets the
     harness actually run your model). Same interface, deliberately different behaviour, for example a
     terser answer style or a more cautious one that escalates sooner. Deterministic, standard library
     only.
   - **A real or on-prem stub.** A class shaped like a real provider adapter: it reads its key from an
     environment variable (for example `LLM_API_KEY`) at call time, and its endpoint from config or the
     environment too. For an offline assignment it need not make a live call; the point is the shape,
     the env-sourced secret, and that it fits the interface. If you build this one, still keep a second
     offline mock available so your harness test can run with no network.
2. **The one-line factory change.** Add your model as a branch in `make_model()`, keyed on its
   `LLM_MODEL` name. Do not restructure the factory; one clean branch is the whole change.
3. **The test (the deliverable proof).** A test that selects your model by name and runs the harness or
   a caller over the golden questions, asserting output for every model and no exception, plus a check
   that `make_model()` with no environment variable still returns `MockModel`.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: write the adapter

Create your model class next to `MockModel` in the model layer. Give it the two methods and nothing the
caller must special-case. If it is a second offline mock, make its behaviour clearly its own so a
comparison is meaningful (a shorter answer, a different escalation threshold), and keep it deterministic
so tests stay stable. If it is a provider stub, read the key with `os.environ.get("LLM_API_KEY")` inside
the method that would call out, and raise a clear error if it is missing, so a misconfigured deployment
fails loudly instead of leaking a blank key.

Hint: the test of a good adapter is that a caller cannot tell which model it holds. If `generate` returns
a `str` and `embed` returns a `list[list[float]]` with one vector per input, in the same shape as
`MockModel`, you have honoured the interface. Anything a caller would have to branch on is a leak in the
seam.

### Level 2: wire the factory

Add one branch to `make_model()` so `LLM_MODEL=<your-name>` returns your model, and confirm the default
path is untouched: with `LLM_MODEL` unset, it still returns `MockModel`. Read the environment inside the
factory, not at import time, so a test can set the variable per case.

Hint: the factory is the only place in the codebase that knows model names. That is deliberate. Every
caller asks `make_model()` for "the model" and gets whatever the environment selected, so switching
models is a deployment setting (one environment variable), never a code change.

### Level 3: run the callers unchanged

Run the comparison harness and the `mock_model` demo with `LLM_MODEL` set to your new name, then with it
unset. The harness should now include your model in its table; the demo should run against your model
with no edit to the demo file. Do not modify a caller to make this work. If a caller needs a change, the
adapter is the thing to fix.

Hint: this is the moment the lesson lands. You changed one class and one factory branch, set one
environment variable, and a harness you did not touch now compares a model it did not know about
yesterday. That is what programming to an interface buys you.

### Level 4: the test

Write a test that:

- sets `LLM_MODEL` to your model's name, calls `make_model()`, and runs the harness (or a caller) over
  the golden questions, asserting every model returns a non-empty answer and no exception is raised;
- confirms the default: with `LLM_MODEL` unset, `make_model()` returns a `MockModel` instance;
- if you built the provider stub, asserts it reads its key from the environment (set a dummy value) and
  raises a clear error when the key is absent, without any key literal appearing in the test.

Keep the existing model-layer tests exactly as they are. They pass unchanged, which is itself the proof
that adding a model disturbed nothing above the interface.

### Level 5: the secret check and commit

Before committing, grep your own change for anything that looks like a key, endpoint, or token. There
should be none: every secret is read from the environment at run time. Then run the tests green, confirm
the harness prints your model in its table when selected, and commit the new adapter, the one-line
factory change, and the test together.

## Done when

- [ ] The new adapter exposes `generate(self, prompt: str) -> str` and `embed(self, texts: list[str]) ->
  list[list[float]]`, in the same shapes as `MockModel`, and nothing else a caller must special-case.
- [ ] `make_model()` returns the new model when `LLM_MODEL=<name>` is set, added as one clean branch.
- [ ] With `LLM_MODEL` unset, `make_model()` still returns the deterministic offline `MockModel`.
- [ ] The comparison harness and the `mock_model` demo run against the new model with no edit to any
  caller.
- [ ] No key, endpoint, or token appears in any committed file; a provider stub reads its key from the
  environment at call time and fails loudly when it is missing.
- [ ] A test selects the new model through the factory, runs the harness or a caller over the golden
  questions with output for every model and no exception, and confirms the unset-default returns
  `MockModel`.
- [ ] The existing model-layer tests pass with no change.

When every box is ticked, you have proven the seam. A new model went in behind the interface, an
environment variable selected it, the harness and the callers ran unchanged, and no secret reached the
repo. That is the whole point of the model layer, and it is the discipline every later session leans on:
the day Sunrise moves the bot to an on-prem model, you change a setting, not the code. The worked
solution is in `solution-02.md` if you want to compare, but try first.
