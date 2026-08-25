"""Measure latency with percentiles (reliability): the average hides the slow tail.

The concept, in plain words:
    If you only track average latency, a handful of very slow requests barely move the
    number, so the dashboard looks calm while some users wait a long time. Percentiles
    tell the real story. p50 is the median (half of requests are faster), p95 and p99
    show how bad it gets for the unlucky few. The gap between p50 and p99 is the tail
    the mean smooths away.

Why a fresher should care:
    Users feel the slow requests, not the average. Watching p95 and p99 catches a
    degrading tail that a steady mean would keep hidden until enough people complain.

What this demo shows:
    A fixed set of 100 latency samples: 96 fast ones around 40 ms and 4 slow ones near
    900 ms. p50 stays with the fast group (41 ms) while p99 lands out in the slow tail
    (930 ms). The mean (76 ms) is dragged up by the outliers and hides the real spread.

Run:  poetry run python demo_latency_percentiles.py
"""

from __future__ import annotations

from statistics import mean


def percentile(sorted_samples: list[int], pct: float) -> int:
    """Return the value at the given percentile using nearest-rank on a sorted list.

    Nearest-rank is the plain textbook method: rank = ceil(pct/100 * n), then
    take that item.
    It needs no interpolation, which keeps the result exact and easy to reason about.
    """
    n = len(sorted_samples)
    rank = max(1, -(-int(pct * n) // 100))  # ceil(pct/100 * n) done with integer math
    return sorted_samples[rank - 1]


def build_samples() -> list[int]:
    """Return 100 fixed latency samples in ms: 96 fast, 4 slow. Deterministic."""
    fast = [38 + (i % 7) for i in range(96)]  # a tight cluster, high 30s to low 40s
    slow = [880, 905, 930, 970]  # the tail: a few requests that took far longer
    return fast + slow


def main() -> None:
    samples = build_samples()
    ordered = sorted(samples)

    avg = mean(samples)
    p50 = percentile(ordered, 50)
    p95 = percentile(ordered, 95)
    p99 = percentile(ordered, 99)

    print(f"samples : {len(samples)} requests (96 fast, 4 slow)")
    print(f"mean    : {avg:6.1f} ms")
    print(f"p50     : {p50:6d} ms")
    print(f"p95     : {p95:6d} ms")
    print(f"p99     : {p99:6d} ms")
    print(
        f"\np50 ({p50} ms) stays with the fast group while p99 ({p99} ms) exposes "
        f"the slow tail; the mean ({avg:.0f} ms) sits between and hides it."
    )


if __name__ == "__main__":
    main()
