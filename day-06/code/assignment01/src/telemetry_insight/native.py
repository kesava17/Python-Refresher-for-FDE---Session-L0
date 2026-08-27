"""The two-language boundary (Day 5): a Python surface over native C code.

Two ideas live here. First, a direct call across the boundary with `ctypes`: Python hands a
byte buffer to the C library's `strlen` and gets a length back. That shows marshaling (a
Python str must be encoded to bytes before it can cross) and the argtypes/restype declarations
that make the crossing safe. Second, a hot step done two ways: a pure-Python CRC32, and the
standard library's `zlib.crc32`, which is the same algorithm written in C. Timing the two shows
why you push a hot loop down into compiled code.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys
import zlib


def _load_libc() -> ctypes.CDLL:
    # The C standard library sits in different places per platform: msvcrt on Windows, and the
    # library named "c" on Linux and macOS. Loading it lets us call C functions directly.
    if sys.platform == "win32":
        return ctypes.CDLL("msvcrt")
    name = ctypes.util.find_library("c")
    if name is None:  # every POSIX system ships a C library; this is a defensive guard
        raise OSError("could not locate the C standard library")
    return ctypes.CDLL(name)


_LIBC = _load_libc()
# Declaring the argument and return types is how ctypes marshals values correctly: strlen takes
# a char* (bytes) and returns a size_t (an unsigned integer). Get these wrong and you get
# garbage or a crash, which is the boundary discipline this whole chapter is about.
_LIBC.strlen.argtypes = [ctypes.c_char_p]
_LIBC.strlen.restype = ctypes.c_size_t


def native_strlen(text: str) -> int:
    """Count the bytes in text by calling C strlen across the boundary, in one coarse crossing."""
    # Marshaling: a Python str is encoded to bytes before it can cross into C.
    return int(_LIBC.strlen(text.encode("utf-8")))


def crc32_python(data: bytes) -> int:
    """A pure-Python CRC32: correct, but the loop runs in the interpreter, one byte at a time."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            # Shift down, and XOR the polynomial only when the low bit was set.
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1))
    return crc ^ 0xFFFFFFFF


def crc32_native(data: bytes) -> int:
    """The same CRC32, computed by zlib's C implementation in a single call across the boundary."""
    return zlib.crc32(data)
