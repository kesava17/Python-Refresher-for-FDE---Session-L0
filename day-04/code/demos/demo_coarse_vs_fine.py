"""Keep the boundary coarse-grained (Level 3.1): cross once for the batch, not once per item.

The concept, in plain words:
    Every crossing into native code has a fixed cost: arguments are marshaled, the call is set up,
    the result is unpacked. That cost is tiny for one call and ruinous for a million. A coarse call
    does the whole batch in one crossing; a fine-grained call pays that fixed cost on every item.

Why a fresher should care:
    The same total work can be fast or slow depending only on how you chunk the boundary. This is
    why a good native wrapper takes a whole array, not one element: it lets you cross once and let
    the compiled side loop, instead of the interpreter looping around a per-item crossing.

What this demo shows:
    The identical bytes are checksummed two ways with the very same zlib.crc32: once over the whole
    blob (one coarse crossing), and once chunk by chunk in a Python loop (many fine crossings).
    Same work, and the single coarse crossing wins.

Run:  poetry run python demo_coarse_vs_fine.py
"""

from __future__ import annotations

import time
import zlib


def main() -> None:
    # One blob of work, split into many small chunks for the fine-grained version.
    chunk = bytes(range(256))  # 256 bytes
    chunks = [chunk] * 4096  # about 1 MB, as 4096 small pieces
    blob = b"".join(chunks)

    # Coarse: hand the whole blob to zlib once. A single crossing, then C loops internally.
    start = time.perf_counter()
    zlib.crc32(blob)
    coarse_seconds = time.perf_counter() - start

    # Fine: call zlib once per small chunk, so the Python loop pays the crossing cost every time.
    start = time.perf_counter()
    running = 0
    for piece in chunks:
        running = zlib.crc32(piece, running)  # chaining keeps the total work identical
    fine_seconds = time.perf_counter() - start

    # Same bytes, same library, same total work: only the grain of the boundary differs.
    print(f"one coarse call (s) : {coarse_seconds:.6f}")
    print(f"{len(chunks)} fine calls (s): {fine_seconds:.6f}")
    ratio = fine_seconds / coarse_seconds if coarse_seconds else float("inf")
    print(f"coarse is           : {ratio:.0f}x faster for the same work")


if __name__ == "__main__":
    main()
