# Solution 02 · Crossing the wall with a hidden layer

> The worked solution for Assignment 02. Try it yourself first. The reference project in
> `code/.../anIntro/assignment02` is verified: ruff and mypy strict are clean and the tests
> pass. There is a correct observation and a correct explanation, and this shows both.

The assignment is about one jump: a hidden layer, trained by backpropagation, solves the exact
problem a single perceptron could not. If you can explain why two lines beat one, and why the
hidden layer needs backpropagation to train, you understand the step that ended the first winter
and started everything after it.

## What a strong answer shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Ran the experiment** | Hidden of two and four reach 100 percent; hidden of one does not. |
| **Read the network** | You can point to `forward` (hidden then output) and the backward updates in `fit`. |
| **Explained capacity** | You say why two lines combine into a boundary one line cannot draw, and why one hidden neuron is short. |
| **Named backpropagation** | You explain that the hidden layer can be trained because the output error is sent back to it. |
| **Met the hazard** | You saw a starting point get stuck and named it a local minimum. |

The trap is to think "more is always better, so use as many hidden neurons as possible." More
capacity does help here, but the real lesson is subtler: two is enough for XOR, one is not, and
a bad starting point can stall even a capable network. Capacity, initialization, and training
all matter together.

## The reference result

Running the experiment (from the `assignment02` folder):

```bash
poetry run python -m tinynn.experiments
```

```text
a two-layer network on XOR, varying the hidden-layer size:

  hidden = 1: accuracy 75%, loss 0.1674
  hidden = 2: accuracy 100%, loss 0.0004
  hidden = 4: accuracy 100%, loss 0.0003
```

And the tests:

```bash
poetry run pytest -q      # 3 passed
poetry run ruff check src tests    # All checks passed!
poetry run mypy src                 # Success: no issues found
```

## The explanation, written out

A single perceptron has one straight line, and XOR cannot be split by one line, so it fails. A
two-layer network changes that:

- Each **hidden neuron** computes its own weighted sum through a sigmoid, so it is its own soft
  line across the input.
- The **output neuron** combines the hidden neurons. With two hidden lines to combine, the
  network can carve out the region between the two XOR diagonals, a bent boundary that no single
  line could form.

That is why **hidden of two** solves XOR (loss near zero, full accuracy) and **hidden of one**
does not: with a single hidden neuron there is still effectively one boundary, not enough to
wrap around XOR, so it stalls at 75 percent. **Hidden of four** also solves it, with a slightly
lower loss, because the extra capacity makes the fit a little easier.

## How the hidden layer is trained

The reason this had to wait until 1986 is training. The hidden neurons are not wired to the
correct answer, so their share of the error is not obvious. In `TwoLayerNet.fit`, the code:

1. runs `forward` to get the hidden values and the output,
2. computes the output error, `d_output`,
3. sends that error back to the hidden layer, `d_hidden`, working out each hidden neuron's
   contribution,
4. updates every weight and bias by a small step against its share of the error.

That backward pass is backpropagation. Without it, there was no reliable way to train the hidden
layer, which is why the escape from the 1969 wall was known in principle for years before it
worked in practice.

## The local-minimum hazard

Train the two-hidden network from a different starting point, for example `TwoLayerNet(hidden=2,
seed=4)`, and it can get stuck around 75 percent with a loss near 0.12: it settled into a poor
solution and cannot climb out with plain gradient descent. This is a **local minimum**. It is a
real training hazard, and it is one reason the field later leaned on better initialization,
more hidden units, and improved optimizers. The reference experiment uses a seed that converges,
but it is worth seeing a stuck run once, so you know it happens.

## Going further (optional)

- Add a fifth logic function of your own and train the two-layer network on it.
- Lower the learning rate and raise the epochs, and see how the loss curve changes.
- Count the weights in the two-hidden network by hand (inputs to hidden, plus hidden to output,
  plus the biases) and check it against the code.
