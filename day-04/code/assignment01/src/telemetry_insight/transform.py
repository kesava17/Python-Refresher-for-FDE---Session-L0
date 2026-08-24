"""A CPU-bound transform over telemetry readings, run three ways.

The point of this module: the work here is CPU-bound (it computes, it does not wait),
so a thread pool cannot speed it up (the GIL), but a process pool can.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

_INNER = 100  # busy-work iterations per value, to make the transform genuinely CPU-bound


def smooth_chunk(values: list[float]) -> float:
    """A deliberately CPU-heavy reduction over a chunk of readings.

    Defined at module top level, so a ProcessPoolExecutor can pickle and run it.
    """
    acc = 0.0
    for value in values:
        for _ in range(_INNER):
            acc += math.sqrt(abs(value) + 1.0) * math.sin(value)
    return acc


def chunk_values(values: Iterator[float], size: int) -> list[list[float]]:
    """Split a stream of values into fixed-size chunks: the unit of parallel work."""
    chunks: list[list[float]] = []
    current: list[float] = []
    for value in values:
        current.append(value)
        if len(current) >= size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def run_serial(chunks: list[list[float]]) -> list[float]:
    """Baseline: one chunk after another."""
    return [smooth_chunk(chunk) for chunk in chunks]


def run_threads(chunks: list[list[float]], workers: int = 8) -> list[float]:
    """Threads: no real speedup here, because the work is CPU-bound (the GIL)."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(smooth_chunk, chunks))


def run_processes(chunks: list[list[float]], workers: int = 8) -> list[float]:
    """Processes: real parallelism, because each has its own interpreter and GIL."""
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(smooth_chunk, chunks))
