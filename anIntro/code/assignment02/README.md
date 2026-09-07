# Assignment 2: cross the wall, and size the hidden layer

Full brief and rubric: `assignment-02.md` and `solution-02.md` (in the content repo).

Train the two-layer network on XOR with different hidden-layer sizes and compare:

```bash
poetry install
poetry run python -m tinynn.experiments
poetry run pytest
```

The `tinynn` package is the one from the live lab. `experiments.py` is the assignment: it solves XOR with a hidden layer and explores how many hidden neurons it takes.
