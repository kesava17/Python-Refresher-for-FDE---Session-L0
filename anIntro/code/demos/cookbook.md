# Demos cookbook: the ANN story, in code you can run

Six short, standard-library demos, one per idea, in the order the story tells them: a neuron,
a perceptron that learns, the wall it hits, the network that climbs over it, the descent that
does the learning, and meaning as vectors. Each shows the command, the output you should see
(captured from a real run), and what to watch for.

Setup once:

```bash
cd demos
poetry install
```

The habit that makes the ideas stick: do not just read the output. **Change a number, predict
what will happen, run it, and check.**

---

## 1. `demo_neuron.py`: a neuron is weights, a sum, an activation

**Concept:** the whole field is built from one unit. It weighs its inputs, adds them, and
fires if the total crosses zero. Change the weights or the bias and the same unit becomes
different logic.

```bash
poetry run python demo_neuron.py
```

**Output:**

```text
weights [1, 1], bias -0.5  ->  this neuron behaves like OR:
  (0, 0) -> 0
  (0, 1) -> 1
  (1, 0) -> 1
  (1, 1) -> 1

weights [1, 1], bias -1.5  ->  harder to fire, now it behaves like AND:
  (0, 0) -> 0
  (0, 1) -> 0
  (1, 0) -> 0
  (1, 1) -> 1
```

**Watch for:** the exact same neuron becoming OR, then AND, only because the bias changed.
Learning is finding those numbers automatically.

**Change it:** set the weights to `[2, -1]` and see which inputs now make it fire.

---

## 2. `demo_perceptron_or.py`: learning weights from examples

**Concept:** the 1958 perceptron does not need the weights set by hand. Shown examples, it
adjusts them a little on every mistake until it classifies OR correctly.

```bash
poetry run python demo_perceptron_or.py
```

**Output:**

```text
  epoch  1: 2 mistake(s), accuracy 50%
  ...
  epoch  6: 1 mistake(s), accuracy 100%
  epoch  7: 0 mistake(s), accuracy 100%

converged: weights [0.13, 0.35], bias -0.10
```

**Watch for:** the mistakes falling to zero. The final weights were learned from the four
examples alone, not written by a person.

**Change it:** switch `OR_DATA` to AND (only `(1, 1)` maps to 1) and confirm it still learns.

---

## 3. `demo_xor_fails.py`: the wall of 1969

**Concept:** XOR is 1 when the inputs differ. Its two classes cannot be split by a single
straight line, and a perceptron only has one line, so it can never reach 100 percent.

```bash
poetry run python demo_xor_fails.py
```

**Output:**

```text
after 50 epochs on XOR:
  best accuracy ever reached: 75%
  final guesses:
    (0, 0) -> guessed 1, correct 0
    (0, 1) -> guessed 1, correct 1
    (1, 0) -> guessed 0, correct 1
    (1, 1) -> guessed 0, correct 0
```

**Watch for:** the accuracy never reaching 100 percent, no matter how long it trains. This is
the limit that froze the field. One of the four is always wrong.

**Change it:** raise `epochs` to 500. It still cannot solve XOR, which is the whole point.

---

## 4. `demo_xor_mlp.py`: crossing the wall with a hidden layer

**Concept:** add one hidden layer of two neurons and train it with backpropagation, and the
network learns XOR, the exact problem the single perceptron could not.

```bash
poetry run python demo_xor_mlp.py
```

**Output:**

```text
  epoch     1: loss 0.2564
  epoch  2000: loss 0.0021
  ...
  epoch  8000: loss 0.0004

final guesses (rounded to 0 or 1):
  (0, 0) -> 0.02 rounds to 0, correct 0
  (0, 1) -> 0.98 rounds to 1, correct 1
  (1, 0) -> 0.98 rounds to 1, correct 1
  (1, 1) -> 0.02 rounds to 0, correct 0

accuracy: 4/4.
```

**Watch for:** the loss falling toward zero and the four outputs snapping to the corners. Two
straight lines, combined by the second layer, carve out what one line could not.

**Change it:** try `TwoLayerNet(seed=4)`. Some starting points get stuck in a poor solution,
a real training hazard the story's later tricks (better initialization, more units) address.

---

## 5. `demo_gradient_descent.py`: how the weights move

**Concept:** backpropagation says which way is downhill; gradient descent takes the steps. The
step size, the learning rate, decides whether training glides to the bottom or bounces out.

```bash
poetry run python demo_gradient_descent.py
```

**Output:**

```text
learning rate 0.1 (sensible): glides toward the bottom
  step 1: x =   0.60, error =     5.76
  ...
  step 6: x =   2.21, error =     0.62

learning rate 1.1 (too large): overshoots and flies apart
  step 1: x =   6.60, error =    12.96
  ...
  step 6: x =  -5.96, error =    80.24
```

**Watch for:** the sensible rate closing in on the lowest point at x = 3, and the large rate
diverging, the error growing every step.

**Change it:** find the largest learning rate that still converges. Somewhere near 1.0 the
behaviour flips.

---

## 6. `demo_embeddings.py`: meaning as numbers

**Concept:** the 2013 idea behind modern language work. Represent each word as a short vector
so that similar meanings sit close together, and similarity becomes distance.

```bash
poetry run python demo_embeddings.py
```

**Output:**

```text
similarity (1.0 = same meaning, 0.0 = unrelated):
  king   vs queen  -> 1.00
  king   vs man    -> 0.74
  king   vs apple  -> 0.00
  man    vs woman  -> 1.00
```

**Watch for:** royal words scoring high with each other and near zero with a fruit. Real
embeddings are learned and have hundreds of numbers, but this is exactly the idea underneath
search, translation, and the retrieval that grounds today's assistants.

**Change it:** add a vector for `prince` and see which words it lands closest to.
