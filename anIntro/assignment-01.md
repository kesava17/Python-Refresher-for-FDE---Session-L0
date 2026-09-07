# Assignment 01 · The perceptron, and the wall it hits

> Offline practice for the introduction. In the live lab you built `tinynn`: a neuron, a
> perceptron that learns, and a two-layer network. Now use the perceptron to feel, for
> yourself, the exact limit that froze the field in 1969. You will train one perceptron on
> three logic problems and watch it sail through two of them and get stuck on the third. No
> mathematics beyond arithmetic, and everything runs offline in pure Python.

This is a do-it-yourself assignment. The point is not to write much code (the perceptron is
already built) but to run a clean experiment and understand what you see: why AND and OR are
learnable by a single straight line, and why XOR is not. When you can explain that in plain
words, you understand linear separability, the idea the whole next chapter of history is built
on.

Start from the `assignment01` project. It carries the `tinynn` package from the live lab and an
`experiments.py` that runs the comparison.

## The goal

One thing, done honestly: train the same perceptron on AND, on OR, and on XOR, and report
whether it converged and what accuracy it reached. Then explain the result. The target output
is a small table like this:

```text
  AND : converged at epoch 9     accuracy 100%
  OR  : converged at epoch 7     accuracy 100%
  XOR : never converged          accuracy 50%
```

AND and OR are linearly separable: a single straight line can split the 1s from the 0s, so the
perceptron finds it and converges. XOR is not: no straight line separates it, so the perceptron
never reaches full accuracy, no matter how long it trains.

## What you have to do

1. **Run the experiment.** Install and run `experiments.py`, and capture the table it prints.
2. **Read the perceptron.** Open `src/tinynn/perceptron.py` and find the three lines in `fit`
   that change the weights and the bias on a mistake. That is the entire learning rule.
3. **Explain the result.** In a few sentences, say why AND and OR converge and XOR does not,
   using the words "linearly separable" and "straight line".
4. **Prove it holds.** Make sure the tests pass: AND and OR reach full accuracy, XOR does not.

## Staged guidance

Work in small steps; check each before moving on.

### Step 1: run it

```bash
cd assignment01
poetry install
poetry run python -m tinynn.experiments
poetry run pytest
```

Capture the table. Confirm AND and OR reach 100 percent and XOR stops at 50 percent.

Hint: the accuracy for XOR may show as 50 percent here. The exact number is not the point; what
matters is that it never reaches 100 percent, however many epochs you allow.

### Step 2: find the learning rule

In `fit`, on each wrong guess the code nudges the weights and the bias toward the right answer:

```python
self.weights[0] += learning_rate * error * x[0]
self.weights[1] += learning_rate * error * x[1]
self.bias += learning_rate * error
```

That is the 1958 perceptron rule in three lines. When a whole pass makes no mistakes, the data
is separated and training stops.

Hint: notice there is nothing XOR-specific being blocked. The rule is willing to learn XOR; the
geometry simply does not allow one straight line to do it.

### Step 3: convince yourself with the picture

Plot the four XOR points by hand: (0,0) and (1,1) are 0, while (0,1) and (1,0) are 1. Try to
draw one straight line with both 1s on one side and both 0s on the other. You cannot. That is
what "not linearly separable" means, and it is exactly why the perceptron is stuck.

Hint: try the same for OR. There, only (0,0) is a 0, so one line easily cuts it off from the
other three. That is why OR converges.

### Step 4: write the explanation

In three or four sentences, explain the table: AND and OR are linearly separable so the
perceptron finds a separating line and converges; XOR is not separable by any single line, so
the perceptron cannot reach full accuracy. Keep it plain.

## Done when

- [ ] `poetry run python -m tinynn.experiments` prints a table where AND and OR converge at 100
  percent and XOR never converges.
- [ ] `poetry run pytest` is green (AND and OR reach full accuracy, XOR does not).
- [ ] You can point to the three lines in `fit` that are the perceptron learning rule.
- [ ] You have written a short, plain explanation using "linearly separable" and "straight
  line".
- [ ] You can say, in one sentence, why this limit mattered so much in 1969.

When every box is ticked, you have felt the wall the founders hit, not just read about it. The
next assignment is about climbing over it. The worked solution is in `solution-01.md` if you
want to compare, but try first.
