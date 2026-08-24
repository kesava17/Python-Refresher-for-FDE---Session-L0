"""Benchmark the pure-Python CRC32 against zlib's native C one, over the sample review text.

This is the second Day 5 proof: pushing a hot loop down into compiled code is measurably
faster. The crossing is coarse-grained, one call over the whole blob, so the boundary cost is
paid once and the C code does the heavy per-byte work.
"""

from __future__ import annotations

import time
from pathlib import Path

from reviews_insight.native import crc32_native, crc32_python


def main() -> None:
    # Read the sample file and repeat it, so there is enough data to time meaningfully.
    sample = Path(__file__).resolve().parents[1] / "data" / "reviews_sample.csv"
    blob = sample.read_bytes() * 400

    start = time.perf_counter()
    crc32_python(blob)
    python_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    crc32_native(blob)
    native_ms = (time.perf_counter() - start) * 1000

    print(f"bytes hashed      : {len(blob)}")
    print(f"pure-Python CRC32 : {python_ms:8.1f} ms")
    print(f"native (zlib) CRC : {native_ms:8.3f} ms")
    speedup = python_ms / native_ms if native_ms else float("inf")
    print(f"speedup           : about {speedup:.0f}x faster in native C")


if __name__ == "__main__":
    main()
