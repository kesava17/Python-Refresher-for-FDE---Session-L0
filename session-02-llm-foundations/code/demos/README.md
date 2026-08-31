# LLM foundations: demos

Five short, offline demos that make the Session 2 concepts visible. No API key, no
network, no cost: a deterministic mock (`mocklib.py`) stands in for a real model.

```bash
poetry install
poetry run python predict.py "where is my"
```

See `cookbook.md` for the full guided walkthrough of all five (`predict.py`,
`tokens.py`, `temperature.py`, `embed_vs_generate.py`, `mock_model.py`), with what to
run, what to watch for, and what to explore.

These demos need only the standard library, so `python <name>.py` also works without
Poetry. The mock is intentionally simple; its job is the concept, not accuracy.
