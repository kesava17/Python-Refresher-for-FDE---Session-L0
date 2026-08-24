"""The two-language boundary (Levels 2.1 and 2.2): call C directly, and marshal the values.

The concept, in plain words:
    Sometimes the code you need is not in Python: it lives in a C library. ctypes lets Python call
    those functions directly. The catch is the boundary: C does not understand a Python str, so you
    must marshal (convert) it to bytes first, and you must tell ctypes the exact argument and
    return types so it packs and unpacks the values correctly.

Why a fresher should care:
    Declaring argtypes and restype is the discipline that keeps the crossing safe. Get them wrong
    and you get garbage or a crash, with no friendly Python traceback. This is the same care every
    foreign-function call needs, in any language.

What this demo shows:
    We load the platform C library, declare that strlen takes a char* and returns a size_t, then
    call it on the bytes for "hello". The marshaling step (str encoded to bytes) is explicit.

Run:  poetry run python demo_ctypes_call.py
"""

from __future__ import annotations

import ctypes
import ctypes.util
import sys


def load_libc() -> ctypes.CDLL:
    """Load the C standard library, which sits in a different place on each platform."""
    # On Windows it is msvcrt; on Linux and macOS it is the library named "c".
    if sys.platform == "win32":
        return ctypes.CDLL("msvcrt")
    name = ctypes.util.find_library("c")
    if name is None:  # every POSIX system ships a C library, so this is a defensive guard
        raise OSError("could not locate the C standard library")
    return ctypes.CDLL(name)


def main() -> None:
    libc = load_libc()

    # Declaring the types is how ctypes marshals correctly: strlen takes a char* (bytes) and
    # returns a size_t (an unsigned integer). Without these, the call is a guess.
    libc.strlen.argtypes = [ctypes.c_char_p]
    libc.strlen.restype = ctypes.c_size_t

    # Marshaling: a Python str is encoded to bytes before it can cross into C.
    text = "hello"
    length = int(libc.strlen(text.encode("utf-8")))

    # The C function counted the bytes for us, across the boundary and back.
    print("native strlen of", repr(text), "->", length)  # 5


if __name__ == "__main__":
    main()
