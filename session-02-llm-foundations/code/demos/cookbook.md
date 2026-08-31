# Demos cookbook: LLM foundations

Five short, offline demos, one per concept. No API key, no network, no cost: a
deterministic mock (`mocklib.py`) stands in for a real model so the idea is visible.

Setup once:

```bash
cd demos
poetry install
```

Then run each demo below. The habit that makes concepts stick: do not just read the
output. **Change the input, predict what will happen, run it, and check.**

---

## 1. `predict.py` — a model predicts the next token

**Concept:** a language model does one thing, over and over: predict the most likely
next token, add it, and repeat.

```bash
poetry run python predict.py "where is my"
```

**Watch for:** the top candidate tokens with probabilities, one being picked, and the
sentence building itself token by token.

**Explore:** try `"is it under"` and `"how do i"`. The guesses change with the context.

---

## 2. `tokens.py` — tokens and cost

**Concept:** models read tokens, not words, and everything is priced per token.

```bash
poetry run python tokens.py "Where is my order SE-1024?"
```

**Watch for:** the sentence split into tokens (punctuation and the order id become
their own tokens), the token count, and a cost estimate.

**Explore:** paste a long paragraph. See how the count and cost jump. That is why we
retrieve only the passages we need instead of sending everything (Session 4).

---

## 3. `temperature.py` — randomness and determinism

**Concept:** the same prompt can give different answers. Temperature is the knob: 0 is
repeatable, higher is varied.

```bash
poetry run python temperature.py
```

**Watch for:** at temperature 0.0 the pick is identical every time; higher up it
varies run to run.

**Explore:** for a support bot, which temperature would you ship? (Low: reliable and
testable.)

---

## 4. `embed_vs_generate.py` — the two model jobs

**Concept:** generation turns text into text (the answer); an embedding turns text
into a meaning vector, so you can search by meaning.

```bash
poetry run python embed_vs_generate.py "how do I return an item?"
```

**Watch for:** the generated sentence, the embedding vector, and that two same-topic
questions have a higher similarity than two different-topic ones.

**Explore:** compare "how do I return this" with "what is your return policy", then
with "where is my order". Same topic sits closer. (Real embeddings arrive in Session 4;
this is a crude stand-in to show the idea.)

---

## 5. `mock_model.py` — the offline model behind one interface

**Concept:** every build runs offline behind a single interface, `generate(prompt)`.
A real or on-prem model plugs in later via an env var, and the caller does not change.

```bash
poetry run python mock_model.py
```

**Watch for:** deterministic answers, and that the warranty question is handled
cautiously (a human would confirm it: the escalation guardrail you build in Session 3).

**Explore:** open `mocklib.py` and read `generate`. This is the seam a real model slots
into in the live lab.
