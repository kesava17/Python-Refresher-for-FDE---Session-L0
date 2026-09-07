# Solution 01 · The perceptron, and the wall it hits

> The worked solution for Assignment 01. Try it yourself first. The reference project in
> `code/.../anIntro/assignment01` is verified: ruff and mypy strict are clean and the tests
> pass. There is no single right paragraph to write; there is a correct observation and a
> correct explanation, and this shows both.

The assignment is not about writing code. It is about seeing, with your own run, why a single
straight line can learn some problems and not others. If you can explain that, you have the one
idea (linear separability) that the whole first winter turns on.

## What a strong answer shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Ran the experiment** | AND and OR converge to 100 percent; XOR never converges. |
| **Found the learning rule** | You can point to the three weight-and-bias updates in `fit`. |
| **Explained separability** | You say, in plain words, that AND and OR can be split by one straight line and XOR cannot. |
| **Used the picture** | You can describe the four XOR points and why no single line separates them. |
| **Read the history** | You connect the result to 1969 and why it stalled the field. |

The trap is to assume the perceptron is "broken" or needs more training. It is not broken, and
more epochs do not help. The problem is geometric: one neuron draws one straight line, and XOR
cannot be split by any straight line. That is the whole lesson.

## The reference result

Running the experiment (from the `assignment01` folder):

```bash
poetry run python -m tinynn.experiments
```

```text
a single perceptron across three logic problems:

  AND : converged at epoch 9     accuracy 100%
  OR  : converged at epoch 7     accuracy 100%
  XOR : never converged          accuracy 50%
```

And the tests:

```bash
poetry run pytest -q      # 2 passed
poetry run ruff check src tests    # All checks passed!
poetry run mypy src                 # Success: no issues found
```

## The explanation, written out

A perceptron classifies by computing `weighted_sum = bias + w1*x1 + w2*x2` and firing when that
sum is at least zero. Geometrically, "the sum is at least zero" is a single straight line: one
side fires, the other does not. So a perceptron can only learn a problem whose 1s and 0s can be
separated by one straight line.

- **AND** has a single 1, at (1, 1). One line easily cuts that corner off from the other three
  points, so the perceptron converges (here at epoch 9).
- **OR** has a single 0, at (0, 0). Again one line separates it from the rest, so the perceptron
  converges (here at epoch 7).
- **XOR** puts the two 1s at (0, 1) and (1, 0), on one diagonal, and the two 0s at (0, 0) and
  (1, 1), on the other diagonal. The classes are interleaved. Whatever straight line you draw,
  one 1 and one 0 always end up on the same side, so at least one of the four is always wrong.
  The perceptron cannot pass 75 percent on any single pass, and it never converges.

## The learning rule

The whole of learning is these three lines in `Perceptron.fit`, applied on every wrong guess:

```python
self.weights[0] += learning_rate * error * x[0]
self.weights[1] += learning_rate * error * x[1]
self.bias += learning_rate * error
```

`error` is the correct answer minus the guess, so it is +1 or -1 on a mistake and 0 when the
guess is right. The weights move toward the correct answer, a little at a time. Nothing here
forbids XOR; the geometry simply makes it impossible for one line.

## Why it mattered in 1969

Minsky and Papert proved this limit and made it famous. Because XOR is about the simplest
interesting problem there is, the conclusion many drew was that the whole approach was a dead
end, and funding and interest collapsed into the first winter. The escape (stack a hidden layer)
was known in principle, but there was no reliable way to train it yet. That is exactly what the
next assignment, and backpropagation, address.

## Going further (optional)

- Change the XOR data to XNOR (1 when the inputs are the same) and confirm the perceptron fails
  on it too, for the same reason.
- Print the learned weights and bias after training on OR, and check by hand that the line they
  describe really does separate the four points.
