# Live lab: build a neural network from scratch that solves XOR

## What we're building

In this lab you build a neural network from nothing but plain Python, and you use it to
re-live the single most important turning point in the history of the field. You will train a
perceptron, the very first learning machine from 1958, and watch it succeed on some problems
and hit a hard wall on one small problem called XOR. That wall is real: it stalled the whole
field for years. Then you will build a two-layer network, add the backpropagation idea from
1986, and watch it walk straight through the same wall.

The project is a tiny Poetry package called `tinynn`. It uses a `src` layout and it is pure
Python: no NumPy, no PyTorch, no TensorFlow, nothing but the standard library. That is on
purpose. Every line of maths is right there in front of you, so nothing is hidden behind a
library you cannot read. By the end you will have trained, by hand, a network that solves the
exact problem a single neuron cannot, and you will understand why the extra layer is what
makes the difference.

Here is the story the code tells, in order:

- **A neuron:** a weighted sum of inputs through a simple on/off activation.
- **A perceptron:** one neuron that learns its own weights from labelled examples.
- **The wall:** the same perceptron trying and failing to learn XOR.
- **A two-layer network:** a hidden layer plus backpropagation that finally learns XOR.

Work in order. Copy, paste, run. After each step there is one line on what happened and why it
matters. You do not need to write any code from scratch; the project is already built and
tested. Your job is to run it, read it, and watch the story unfold.

## Ground rules

- Everything Python runs through `poetry run`. This guarantees you are using the project's own
  environment and not some other Python on your machine.
- Run every command from inside the `liveLab/` folder (the folder that holds `pyproject.toml`).
- The whole lab is fully offline. Once dependencies are installed there is no network call
  anywhere, so it runs the same on a plane as on your desk.
- It is pure Python. The only tools involved are the dev tools (pytest, ruff, mypy); the
  network itself uses nothing but the standard library.

---

## Step 0: set up and run offline

First install the project, then run the three quality gates. This is your baseline: if the
tests are green and the linters are clean before you touch anything, then any red you see later
is something worth understanding, not something you inherited.

```bash
cd liveLab
poetry install
poetry run pytest
poetry run ruff check src tests
poetry run mypy src
```

You should see the test run report **8 passed**, and both `ruff` and `mypy` finish clean with
no complaints.

The eight tests cover all three pieces of the story: that the datasets hold the truth tables we
expect, that the perceptron learns the separable problems and fails on XOR, and that the
two-layer network learns XOR and drives its error down while training.

Notice what was not installed: no maths library, no machine-learning framework. Look at
`pyproject.toml` and you will see the only runtime requirement is Python itself (`python = "^3.11"`).
Everything else in the file is a development tool. This is a neural network with zero learning
libraries behind it.

**What happened.** You have a green project running entirely on standard-library Python, so
every result from here on is something the code in front of you produced, with nothing hidden.

---

## Step 1: the datasets

Open `src/tinynn/data.py`. This is the smallest possible file, and it is where the whole lesson
begins. It defines three classic logic problems, each as four labelled examples. An example is a
pair of 0/1 inputs and the correct 0/1 output.

```python
Example = tuple[tuple[int, int], int]

AND: list[Example] = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
OR:  list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 1)]
XOR: list[Example] = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]
```

Read these as truth tables. **AND** is 1 only when both inputs are 1. **OR** is 1 when either
input is 1. **XOR**, exclusive or, is 1 exactly when the two inputs differ.

There is a hidden property here that decides the entire lab. AND and OR are **linearly
separable**: if you plot the four points on a square, you can draw a single straight line that
puts every 1 on one side and every 0 on the other. XOR is **not** linearly separable: the two 1s
sit on opposite corners, so no single straight line can separate the 1s from the 0s. Keep that
picture in mind. A single perceptron can only ever draw one straight line, and that is exactly
why it will be able to learn AND and OR but never XOR.

**What happened.** You met the three problems, and you saw that XOR is the odd one out: it is
the one no single straight line can solve.

---

## Step 2: one neuron

Open `src/tinynn/neuron.py`. A neuron is simpler than it sounds. It takes some inputs, weighs
each one, adds them up with a bias, and then decides whether to fire. That is the whole idea, and
it fits in two small functions.

```python
def step(total: float) -> int:
    """The activation: fire (1) if the total is at least zero, otherwise 0."""
    return 1 if total >= 0.0 else 0


def weighted_sum(inputs: list[float], weights: list[float], bias: float) -> float:
    """Combine inputs and weights into one number: bias plus the sum of weight times input."""
    return bias + sum(w * x for w, x in zip(weights, inputs, strict=True))
```

`weighted_sum` is the "how strongly do I feel about this input" part. Each input is multiplied by
its own weight, all of those products are added together, and the bias is added on top as a
baseline. The bias lets the neuron shift its decision point up or down regardless of the inputs.

`step` is the decision. It looks at that single total and answers with a plain 1 or 0: fire, or do
not fire. If the total reaches zero or goes above it, the neuron outputs 1; otherwise 0. This
sharp on/off behaviour is the classic perceptron activation.

Together these two functions are a complete neuron. The weights and bias are just numbers, and
learning, which comes next, is nothing more than nudging those numbers until the neuron gives the
right answers.

**What happened.** You saw that a neuron is a weighted sum followed by a yes/no decision, and
that its behaviour is fully controlled by a handful of numbers.

---

## Step 3: the perceptron learns

Open `src/tinynn/perceptron.py`. A perceptron is one neuron that can learn its own weights from
examples, using a rule Frank Rosenblatt published in 1958. It starts from small random weights
and a zero bias, and every time it guesses wrong it corrects itself a little.

Here is the heart of it, the `fit` method:

```python
def fit(self, data: list[Example], epochs: int = 20, learning_rate: float = 0.1) -> int:
    """Train with the perceptron rule. Return the epoch it converged, or -1 if it did not."""
    for epoch in range(1, epochs + 1):
        mistakes = 0
        for x, target in data:
            error = target - self.predict(x)
            if error != 0:
                mistakes += 1
                self.weights[0] += learning_rate * error * x[0]
                self.weights[1] += learning_rate * error * x[1]
                self.bias += learning_rate * error
        if mistakes == 0:
            return epoch
    return -1
```

Read it in plain words. For each example, it compares the correct answer to its own guess and
computes the `error`. If the error is zero the guess was right and nothing changes. If the error
is not zero, it nudges each weight and the bias in the direction that would have made the guess
better, by a small amount controlled by the `learning_rate`. One full pass over all four examples
is one "epoch". The moment a whole pass makes no mistakes, the data is separated, learning is
done, and it returns the epoch number. If it burns through all its epochs still making mistakes,
it returns `-1` to say it never converged.

Now watch it learn. Start an interactive Python session inside the project and train a perceptron
on OR:

```bash
poetry run python
```

```python
from tinynn.data import OR
from tinynn.perceptron import Perceptron

model = Perceptron(seed=1)
converged = model.fit(OR)
print("converged at epoch", converged)
print("accuracy", model.accuracy(OR))
```

You will see it converge in a handful of epochs and reach an accuracy of `1.0`, meaning it gets
all four OR examples right. It found a straight line that separates the 1s from the 0, exactly as
promised, because OR is linearly separable. Type `exit()` to leave the session.

**What happened.** You watched a single neuron teach itself, from labelled examples alone, to
solve OR perfectly, just by nudging a few numbers whenever it was wrong.

---

## Step 4: the wall

Now for the moment that changed the field. Take the same perceptron, the same learning rule, the
same everything, and point it at XOR instead of OR. Start Python again:

```bash
poetry run python
```

```python
from tinynn.data import XOR
from tinynn.perceptron import Perceptron

model = Perceptron(seed=1)
converged = model.fit(XOR, epochs=200)
print("converged at epoch", converged)
print("accuracy", model.accuracy(XOR))
```

Watch what happens. Even with 200 epochs, `converged` comes back as `-1`: it never converged. The
accuracy stalls at `0.5`, which is 50 percent, no better than a coin toss. Run it with even more
epochs if you like. It will not help. The perceptron is physically incapable of solving XOR, and
no amount of extra training changes that.

This is not a bug in the code, and it is not a bad choice of learning rate. It is a hard
mathematical limit. A single perceptron can only draw one straight line, and XOR cannot be split
by any single straight line. In 1969, Marvin Minsky and Seymour Papert wrote this limitation down
in a book, and the field's optimism collapsed for years. You are now feeling that exact wall
first-hand, in code you can read top to bottom. Type `exit()` to leave.

**What happened.** You watched the perceptron fail on XOR no matter how long it trained, and you
saw firsthand the 1969 limit that stopped the whole field: one neuron, one straight line, and XOR
needs more than that.

---

## Step 5: the two-layer network breaks through

Open `src/tinynn/mlp.py`. The fix, it turns out, is not a smarter neuron. It is more neurons,
arranged in layers. This file builds a `TwoLayerNet`: two inputs, a small hidden layer of neurons
in the middle, and one output neuron. The hidden layer is the key. It lets the network bend its
decision boundary instead of being stuck with one straight line.

Two things change from the perceptron. First, the activation is now a smooth `sigmoid` instead of
the sharp step:

```python
def sigmoid(z: float) -> float:
    """A smooth activation between 0 and 1, so error can flow back through the layers."""
    return 1.0 / (1.0 + math.exp(-z))
```

The smoothness matters. A sharp step has no slope to follow, but sigmoid does, and that slope is
what lets the network figure out which direction to adjust each weight. `forward` runs an input
through both layers to produce a guess:

```python
def forward(self, x: tuple[float, float]) -> tuple[list[float], float]:
    """Compute the hidden activations and the final output for one input."""
    hidden = [
        sigmoid(self.b1[j] + self.w1[j][0] * x[0] + self.w1[j][1] * x[1]) for j in range(self.hidden)
    ]
    output = sigmoid(self.b2 + sum(self.w2[j] * hidden[j] for j in range(self.hidden)))
    return hidden, output
```

Each hidden neuron does its own weighted sum of the two inputs and passes it through sigmoid. The
output neuron then does a weighted sum of the hidden neurons' answers. The input has now passed
through two layers, and that is enough to represent XOR.

The second change is how it learns. The perceptron could only adjust one layer, but here the
error has to reach back through two. That is backpropagation, the 1986 idea, and it is the heart
of `fit`:

```python
def fit(self, data: list[Example], epochs: int = 8000, learning_rate: float = 0.5) -> None:
    """Train with online backpropagation: for each example, push the error backward and step."""
    for _ in range(epochs):
        for x, target in data:
            point = (float(x[0]), float(x[1]))
            hidden, output = self.forward(point)
            d_output = (output - target) * output * (1.0 - output)
            d_hidden = [d_output * self.w2[j] * hidden[j] * (1.0 - hidden[j]) for j in range(self.hidden)]
            for j in range(self.hidden):
                self.w2[j] -= learning_rate * d_output * hidden[j]
            self.b2 -= learning_rate * d_output
            for j in range(self.hidden):
                self.w1[j][0] -= learning_rate * d_hidden[j] * point[0]
                self.w1[j][1] -= learning_rate * d_hidden[j] * point[1]
                self.b1[j] -= learning_rate * d_hidden[j]
```

Read it as two motions. First it computes `d_output`, how wrong the final answer was and which way
to correct it. Then it sends that error backward into the hidden layer as `d_hidden`, working out
how much each hidden neuron contributed to the mistake. Now that it knows the blame for every
weight in both layers, it nudges them all a little in the improving direction. That backward flow
of error, from the output all the way to the hidden layer, is the whole trick that a single
perceptron never had.

Now watch it break through the wall. Start Python and train it on the very problem the perceptron
could not touch:

```bash
poetry run python
```

```python
from tinynn.data import XOR
from tinynn.mlp import TwoLayerNet

net = TwoLayerNet(hidden=2, seed=1)
net.fit(XOR)
print("accuracy", net.accuracy(XOR))
print("loss", net.loss(XOR))
```

The accuracy comes back as `1.0`: all four XOR examples correct, the same problem the perceptron
was stuck at 50 percent on. The `loss`, which measures how far the network's outputs are from the
targets on average, has dropped to nearly zero. Type `exit()` to leave.

**What happened.** By adding one hidden layer and training it with backpropagation, the network
solved XOR completely, walking straight through the wall that stopped a single perceptron.

---

## Step 6: run it all at once

You have now seen each piece on its own. The project also ships one command that runs the whole
story end to end, so you can see the three results side by side. Open `src/tinynn/run.py` to see
that it does exactly what you just did by hand: trains a perceptron on OR, the same perceptron on
XOR, then a two-layer network on XOR. Run it:

```bash
poetry run python -m tinynn.run
```

```text
perceptron on OR : converged at epoch 7, accuracy 100%
perceptron on XOR: accuracy 50%, it cannot reach 100 percent
two-layer on XOR : accuracy 100%, loss 0.0004
```

Read those three lines top to bottom, because they are the entire history of early neural networks
in miniature. The perceptron learns OR in 7 epochs and nails it, 100 percent. The same perceptron
on XOR is stuck at 50 percent and, as the line says, cannot reach 100 percent no matter what. Then
the two-layer network takes on XOR and reaches 100 percent, with the loss driven all the way down
to 0.0004.

**What happened.** One command replayed the whole arc: a perceptron that learns, the wall it
cannot cross, and the two-layer network that crosses it.

---

## You should see

Run through this recap. If each line matches, the lab is done and you have built a working neural
network from scratch.

- `poetry run pytest` reports **8 passed**, and both `poetry run ruff check src tests` and
  `poetry run mypy src` finish clean.
- The whole thing ran offline, on pure standard-library Python, with no maths or
  machine-learning library anywhere in `pyproject.toml`.
- **The datasets:** AND, OR, and XOR are each four labelled examples; AND and OR are linearly
  separable, and XOR is not.
- **The neuron:** a weighted sum of inputs plus a bias, passed through a step activation, is a
  complete neuron controlled entirely by its numbers.
- **The perceptron:** on OR it converges and reaches 100 percent, learning a straight line from
  examples alone.
- **The wall:** on XOR the same perceptron never converges and sits at 50 percent, the 1969 limit
  felt first-hand.
- **The two-layer network:** on XOR it reaches 100 percent with the loss near zero, because a
  hidden layer trained by backpropagation can bend the boundary a single line cannot.
- `poetry run python -m tinynn.run` prints the three lines exactly:

```text
perceptron on OR : converged at epoch 7, accuracy 100%
perceptron on XOR: accuracy 50%, it cannot reach 100 percent
two-layer on XOR : accuracy 100%, loss 0.0004
```

That is the point of the whole build. You trained, from scratch and in pure Python, a network
that solves the exact problem (XOR) that a single perceptron cannot. That jump, from one layer
that draws a single straight line to a network with a hidden layer that learns by pushing its
error backward, is the entire jump from a single neuron to a deep network. Every modern neural
network, however large, is built on the same two ideas you just watched work: stack layers so the
model can represent more, and train them with backpropagation so every layer learns. You have now
seen both, not as formulas in a slide, but as code you ran and numbers you watched change.
