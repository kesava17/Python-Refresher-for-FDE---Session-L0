# Assignment 1: the perceptron and the wall

Full brief and rubric: `assignment-01.md` and `solution-01.md` (in the content repo).

Run the experiment across AND, OR, and XOR, and see where a single perceptron stops:

```bash
poetry install
poetry run python -m tinynn.experiments
poetry run pytest
```

The `tinynn` package is the one from the live lab. `experiments.py` is the assignment: it trains the perceptron on each logic problem and reports whether it converged.
