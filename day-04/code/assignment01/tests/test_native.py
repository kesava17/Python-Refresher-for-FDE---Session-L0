"""Day 5 native-boundary tests: the compiled path agrees with the pure-Python one."""

from __future__ import annotations

import zlib

from telemetry_insight.native import crc32_native, crc32_python, native_strlen


def test_crc32_python_matches_native() -> None:
    # The pure-Python CRC32 and zlib's C CRC32 are the same algorithm, so they must agree.
    for text in ["", "hello", "telemetry-insight", "D100,20.5"]:
        data = text.encode("utf-8")
        assert crc32_python(data) == zlib.crc32(data) == crc32_native(data)


def test_native_strlen_matches_len_for_ascii() -> None:
    # Across the ctypes boundary, C strlen counts the same bytes Python does for ASCII text.
    assert native_strlen("hello") == 5
    assert native_strlen("") == 0
