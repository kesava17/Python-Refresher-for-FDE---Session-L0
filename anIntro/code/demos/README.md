# ANN introduction: demos

Six tiny, runnable demos, one idea each, standard library only, no setup beyond Python. They
turn the story from the deck into something you can run: a neuron, a perceptron that learns,
the XOR wall, a two-layer network that crosses it, gradient descent, and embeddings.

```bash
poetry install
poetry run python demo_perceptron_or.py
```

| Demo | The idea | You should see |
| --- | --- | --- |
| `demo_neuron.py` | a neuron is weights, a sum, an activation | one unit acting as OR, then as AND, just by changing the bias |
| `demo_perceptron_or.py` | learning weights from examples (1958) | the perceptron converge to 100 percent on OR |
| `demo_xor_fails.py` | the linear-separability wall (1969) | a single perceptron stuck at 75 percent on XOR |
| `demo_xor_mlp.py` | hidden layers and backpropagation (1986) | a 2-2-1 network reach 4/4 on XOR as the loss falls |
| `demo_gradient_descent.py` | how weights move downhill | a good learning rate converge, a large one diverge |
| `demo_embeddings.py` | meaning as vectors (2013) | similar words score near 1.0, unrelated ones near 0.0 |

See `cookbook.md` for the guided walkthrough of all six, with what to run, what to watch for,
and what to change. Everything runs offline with `python <name>.py` too; the demos need only
the standard library. The code is pure Python on purpose, so you can read every line.
