# Assignment 02 · Crossing the wall with a hidden layer

> Offline practice for the introduction. In Assignment 1 you watched a single perceptron fail
> on XOR. Now you cross that wall. Using the two-layer network from the live lab, you will solve
> XOR, and then explore how many hidden neurons it takes and why one is not enough. This is the
> jump from a single layer to a deep network, felt firsthand. Everything runs offline in pure
> Python.

This is a do-it-yourself assignment. The network and backpropagation are already built in
`tinynn`; your job is to run the experiment, read the result, and understand it: that a hidden
layer lets two straight lines combine into a boundary a single line could never draw, and that
capacity (the number of hidden neurons) matters.

Start from the `assignment02` project. It carries the `tinynn` package from the live lab and an
`experiments.py` that trains the two-layer network on XOR with different hidden-layer sizes.

## The goal

One thing, done honestly: train the two-layer network on XOR with one, two, and four hidden
neurons, and report the accuracy and loss for each. Then explain why one is not enough and two
is. The target output is a small table like this:

```text
  hidden = 1: accuracy 75%, loss 0.1674
  hidden = 2: accuracy 100%, loss 0.0004
  hidden = 4: accuracy 100%, loss 0.0003
```

One hidden neuron still cannot bend the boundary enough, so it stalls short of full accuracy.
Two hidden neurons are the classic minimum that solves XOR, and more make training easier and
the loss a little lower.

## What you have to do

1. **Run the experiment.** Install and run `experiments.py`, and capture the table.
2. **Read the network.** Open `src/tinynn/mlp.py`. Find `forward` (how the hidden layer feeds
   the output) and the backpropagation updates in `fit` (how the error is pushed back to every
   weight).
3. **Explain the result.** In a few sentences, say why a hidden layer can solve XOR when a
   single perceptron cannot, and why one hidden neuron is not enough.
4. **Prove it holds.** Make sure the tests pass: hidden of two and of four solve XOR, hidden of
   one does not.

## Staged guidance

Work in small steps; check each before moving on.

### Step 1: run it

```bash
cd assignment02
poetry install
poetry run python -m tinynn.experiments
poetry run pytest
```

Capture the table. Confirm hidden of two and four reach 100 percent, and hidden of one does not.

### Step 2: see how the layers combine

In `forward`, each hidden neuron computes its own weighted sum through a sigmoid, and the output
neuron combines the hidden values. Two hidden neurons give you two lines; the output neuron
combines them into a bent boundary that can wrap around the XOR pattern.

Hint: think back to the picture. One line cannot separate the two diagonals of XOR. Two lines,
combined, can carve out the region between them. The hidden layer is those two lines; the output
layer is the combination.

### Step 3: see backpropagation adjust the hidden layer

In `fit`, the code computes the output error, then sends it back to the hidden layer
(`d_hidden`), then updates every weight. This backward pass is what makes it possible to train
the hidden layer at all, the missing piece that kept the field frozen until 1986.

Hint: the hidden neurons are not connected directly to the right answer, so their share of the
error has to be worked out from the output error. That is exactly what backpropagation does.

### Step 4: explore, and meet a real hazard

Try changing the seed on the two-hidden-neuron network (for example `TwoLayerNet(hidden=2,
seed=4)` in a quick script). Some starting points get stuck in a poor solution and do not reach
full accuracy. This is a real training hazard called a local minimum, and it is one reason more
hidden neurons and better starting points help.

Hint: this is why the story later needed better initialization and larger networks. Capacity and
a good start are not luxuries; they make training reliable.

### Step 5: write the explanation

In three or four sentences, explain the table: a single perceptron has one line and fails on
XOR; a hidden layer gives several lines that combine into a bent boundary, so two or more hidden
neurons solve it; one hidden neuron does not have enough capacity. Mention that backpropagation
is what trains the hidden layer.

## Done when

- [ ] `poetry run python -m tinynn.experiments` prints a table where hidden of two and four
  reach 100 percent and hidden of one does not.
- [ ] `poetry run pytest` is green (two and four hidden solve XOR, one does not).
- [ ] You can point to `forward` and to the backpropagation updates in `fit`.
- [ ] You have written a short, plain explanation of why a hidden layer solves XOR and why one
  neuron is not enough.
- [ ] You have seen at least one starting point get stuck, and can name it as a local minimum.

When every box is ticked, you have crossed the wall the founders could not, with the same idea
(a hidden layer trained by backpropagation) that ended the first winter and opened the road to
deep learning. The worked solution is in `solution-02.md` if you want to compare, but try first.
