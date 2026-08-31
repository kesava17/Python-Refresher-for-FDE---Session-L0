# Assignment 1: compare three model configurations and defend a pick

Full brief and rubric: `assignment-01.md` and `solution-01.md` (in the content repo).

You are given the model layer and the comparison harness. Configure three candidate
models, run them against the shared golden question set, and write a one-paragraph
recommendation that names the winner and why (capability on the golden set, cost,
latency, and Bharat residency as a hard gate). Everything runs offline, no API key.

```bash
poetry install
# edit CANDIDATES in my_comparison.py, then:
poetry run python my_comparison.py
poetry run pytest
```

Deliverable: the comparison table your run produces, plus your defended recommendation.
