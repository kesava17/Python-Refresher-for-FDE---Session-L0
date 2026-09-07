# tinynn (live lab)

A tiny neural network, built from scratch in pure Python, that turns the introduction's story
into code you can run and read. No third-party libraries.

```bash
poetry install
poetry run python -m tinynn.run      # the whole story in three lines of output
poetry run pytest                    # the tests
poetry run ruff check src tests
poetry run mypy src
```

## What is here

```
src/tinynn/
  data.py         the AND, OR, and XOR datasets
  neuron.py       one neuron: a weighted sum through a step
  perceptron.py   a perceptron that learns its weights (learns OR, fails XOR)
  mlp.py          a two-layer network trained by backpropagation (learns XOR)
  run.py          trains all three and prints the result
tests/            perceptron, mlp, and dataset tests
```

## What it shows

```text
perceptron on OR : converged at epoch 7, accuracy 100%
perceptron on XOR: accuracy 50%, it cannot reach 100 percent
two-layer on XOR : accuracy 100%, loss 0.0004
```

The perceptron learns OR from examples alone, because OR can be split by one straight line. It
cannot learn XOR, because no single line separates it: this is the wall of 1969. Add one hidden
layer and train it with backpropagation, and the same problem is solved: this is the step that
ended the first winter and opened the road to deep learning.

The code is pure Python on purpose. Real work uses libraries like PyTorch, but here you can
read every weight update and see exactly how a network learns.
