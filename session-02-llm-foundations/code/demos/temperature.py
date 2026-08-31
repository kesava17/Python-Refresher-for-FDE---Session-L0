"""Demo: temperature, randomness, and determinism.

The same prompt can give different answers. Temperature is the knob. At 0 the model
takes the most likely token every time (repeatable). Higher, it samples (varied).

Run:  poetry run python temperature.py
"""

from __future__ import annotations

import random

from mocklib import next_token_probs


def sample(dist: list[tuple[str, float]], temperature: float) -> str:
    """Pick one token from the distribution, greedily at temperature 0 else sampled."""
    if temperature <= 0.0:
        return dist[0][0]  # greedy: always the most likely token
    # crude temperature: flatten the distribution, then sample
    weights = [p ** (1.0 / temperature) for _, p in dist]
    total = sum(weights) or 1.0
    r = random.random() * total
    upto = 0.0
    for (token, _), w in zip(dist, weights):
        upto += w
        if r <= upto:
            return token
    return dist[-1][0]


def run(temperature: float, times: int = 5) -> None:
    """Sample the next token several times at one temperature and print the picks."""
    dist = next_token_probs("where is my")
    picks = [sample(dist, temperature) for _ in range(times)]
    print(f"temperature {temperature}:  {picks}")


def main() -> None:
    """Show how the same prompt varies across low and high temperatures."""
    print('context: "where is my", asked five times at each temperature\n')
    run(0.0)
    run(0.7)
    run(1.2)
    print()
    print("At 0.0 the answer is identical every time; higher up it varies.")
    print("For support answers you want low temperature: reliable and testable.")


if __name__ == "__main__":
    main()
