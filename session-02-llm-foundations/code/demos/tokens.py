"""Demo: how a model sees text as tokens, and what that costs.

Models do not read words or characters; they read tokens. Everything is counted and
priced in tokens. This shows the split, the count, and a cost estimate.

Run:  poetry run python tokens.py "Where is my order SE-1024?"
"""

from __future__ import annotations

import sys

from mocklib import PRICE_PER_1K, count_tokens, estimate_cost, tokenize


def main() -> None:
    """Tokenize the input text and print its token split, count, and cost estimate."""
    text = sys.argv[1] if len(sys.argv) > 1 else "Where is my order SE-1024?"
    toks = tokenize(text)
    n = count_tokens(text)
    cost = estimate_cost(n)

    print(f'text: "{text}"')
    print(f"tokens ({n}): {toks}")
    print(f"characters: {len(text)}   tokens: {n}   (~{len(text) / max(n, 1):.1f} chars per token)")
    print(f"cost estimate: Rs {cost:.4f} at Rs {PRICE_PER_1K} per 1,000 tokens")
    print()
    print("Notice: punctuation and the order id become their own tokens, and a long")
    print("context (a whole help article) would cost far more than a short question.")


if __name__ == "__main__":
    main()
