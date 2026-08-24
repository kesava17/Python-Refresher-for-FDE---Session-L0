"""Push a hot loop into compiled code (Level 3.2): the same CRC32, two speeds.

The concept, in plain words:
    A pure-Python loop runs one step at a time inside the interpreter, which is fine until the loop
    is huge and hot. The same algorithm written in C runs the whole loop in compiled code and hands
    back one answer. zlib.crc32 is exactly that: the CRC32 algorithm, in C, in the standard library.

Why a fresher should care:
    You do not rewrite your whole program in C. You find the one hot loop, and you call a compiled
    version of just that. Timing the two side by side shows how large the gap is, so you can decide
    when the boundary crossing is worth it.

What this demo shows:
    A pure-Python crc32 and zlib.crc32 compute the same checksum over the same few-hundred-KB blob.
    Both answers match (same algorithm); the compiled one is far faster, and we print the speedup.

Run:  poetry run python demo_native_speed.py
"""

from __future__ import annotations

import time
import zlib


def crc32_python(data: bytes) -> int:
    """A pure-Python CRC32: correct, but the loop runs in the interpreter, one byte at a time."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            # Shift down, and XOR the polynomial only when the low bit was set.
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1))
    return crc ^ 0xFFFFFFFF


def main() -> None:
    # A few hundred KB is enough to make the interpreter loop's cost obvious.
    blob = bytes(range(256)) * 1024  # 256 KB of predictable bytes

    # Time the pure-Python version: every byte is handled by interpreted code.
    start = time.perf_counter()
    py_result = crc32_python(blob)
    py_seconds = time.perf_counter() - start

    # Time the C version: one call crosses into compiled code and does the whole loop there.
    start = time.perf_counter()
    c_result = zlib.crc32(blob)
    c_seconds = time.perf_counter() - start

    # Same algorithm, so the checksums must agree. Speed is the only thing that changed.
    print("results match       :", py_result == c_result)
    print(f"pure Python (s)     : {py_seconds:.4f}")
    print(f"zlib in C   (s)     : {c_seconds:.6f}")
    speedup = py_seconds / c_seconds if c_seconds else float("inf")
    print(f"speedup             : {speedup:.0f}x faster in C")


if __name__ == "__main__":
    main()
