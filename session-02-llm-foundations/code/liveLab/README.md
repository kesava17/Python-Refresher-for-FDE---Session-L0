# Model layer (live lab)

The first layer of the Sunrise Support Deflection Assistant: one small interface with a
pluggable model behind it, plus a harness that picks a model on evidence. Fully offline
by default (a deterministic mock, no API key), with a real or on-prem adapter that plugs
in behind the same interface via the `LLM_MODEL` environment variable.

```bash
poetry install
poetry run python -m model_layer.compare   # compare candidate models on the golden set
poetry run pytest                           # run the tests
```

## What is here

```
src/model_layer/
  model.py     the Model interface, the deterministic MockModel, the RealModel seam, make_model()
  corpus.py    load the shared help corpus and golden question set
  compare.py   the model-comparison harness (offline: three mock capability levels)
data/
  help_corpus.json      the Sunrise help articles (shared across the whole phase)
  golden_questions.csv  the labelled golden question set (shared across the whole phase)
tests/         tests for the model layer and the corpus
```

## Offline by default, real when you want

`make_model()` returns the offline mock unless you set `LLM_MODEL`. To point at a real or
on-prem model, set the environment (never commit a key):

```bash
export LLM_MODEL=real
export LLM_PROVIDER=your-provider
export LLM_API_KEY=your-key   # from a secret store, not the repo
```

The `RealModel` adapter is a seam: wire your provider's SDK call inside it. Nothing else
in the assistant changes, because everything calls the same `generate` and `embed`.

## The shared backbone

`data/help_corpus.json` and `data/golden_questions.csv` are created here and reused by
every later session (prompting, RAG grounding, the eval harness, the assembled PoC). The
golden set deliberately marks the sensitive warranty questions and the out-of-scope ones
for escalation, so a model is scored on escalating cleanly as well as answering.
