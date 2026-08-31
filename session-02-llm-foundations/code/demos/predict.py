"""Demo: watch a model predict the next token, one step at a time.

A language model does one thing, over and over: given the text so far, predict the
most likely next token, add it, and repeat. This shows that loop with probabilities.

Run:  poetry run python predict.py "where is my"
      poetry run python predict.py "is it under"
"""

from __future__ import annotations

import sys

from mocklib import next_token_probs, tokenize


def main() -> None:
    """Run the next-token prediction loop for a few steps and print the tokens."""
    context = sys.argv[1] if len(sys.argv) > 1 else "where is my"
    print(f'context: "{context}"\n')

    for step in range(3):
        dist = next_token_probs(context)
        print(f"step {step + 1}: next-token candidates")
        for token, prob in dist:
            bar = "#" * int(prob * 30)
            print(f"    {token:<10} {prob:>4.2f} {bar}")
        best = dist[0][0]
        context = f"{context} {best}"
        print(f'    -> picked "{best}"   context is now: "{context}"\n')

    print(f"tokens so far: {tokenize(context)}")


if __name__ == "__main__":
    main()
