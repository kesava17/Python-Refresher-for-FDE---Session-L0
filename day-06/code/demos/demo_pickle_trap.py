"""Unsafe deserialization (security): pickle can run code; JSON plus a schema cannot.

The concept, in plain words:
    pickle is Python's "turn bytes back into objects" format, and it is powerful in a
    dangerous way: unpickling can execute code the sender chose. A crafted pickle
    payload can run a command the moment you load it, before you inspect anything. So
    pickle is only safe for data you fully trust. For anything from the outside (a
    request body, a cache someone else can write, a file upload), use a data-only format
    like JSON and then validate the shape yourself. JSON parsing cannot call functions;
    it only builds strings, numbers, lists, and dicts.

Why a fresher should care:
    "Just pickle it" shows up in caches, queues, and session stores, and it silently
    becomes a remote-code-execution hole the day an attacker can influence those bytes.
    The safe habit is simple: untrusted input travels as JSON, and you check its shape
    before trusting it.

What this demo shows:
    A crafted pickle payload whose only side effect is writing a harmless sentinel file
    (standing in for "arbitrary code ran"). Loading it runs that code. The same review
    as JSON, loaded and schema-checked, never executes anything, and the check confirms
    the shape. The test proves the JSON path leaves no sentinel and validates the
    fields.

Run:  poetry run pytest demo_pickle_trap.py -v
"""

from __future__ import annotations

import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any

# A file that "arbitrary code" will create if a payload manages to execute on load.
# Its presence is our stand-in for "the attacker's code ran".
SENTINEL = Path(tempfile.gettempdir()) / "demo_pickle_sentinel.txt"


class _CraftedPayload:
    """A malicious object. __reduce__ tells pickle what to run when it is loaded."""

    def __reduce__(self) -> tuple[Any, ...]:
        # On load, pickle calls the returned callable. Here it writes a sentinel file.
        # A real attacker would run any command they liked instead.
        return (_write_sentinel, ())


def _write_sentinel() -> int:
    SENTINEL.write_text("arbitrary code ran during unpickling\n", encoding="utf-8")
    return 0


def load_pickle(blob: bytes) -> Any:
    """UNSAFE: unpickling untrusted bytes can execute code chosen by the sender."""
    return pickle.loads(blob)


def load_json_reviewed(text: str) -> dict[str, Any]:
    """SAFE: parse JSON (data only), then check the shape before trusting it."""
    parsed = json.loads(text)  # can only build str/num/list/dict, never runs code
    if not isinstance(parsed, dict):
        raise ValueError("expected a JSON object")
    # A minimal schema check: required fields with the right types.
    if not isinstance(parsed.get("product_id"), str):
        raise ValueError("product_id must be a string")
    if not isinstance(parsed.get("rating"), int):
        raise ValueError("rating must be an integer")
    return parsed


def _clear_sentinel() -> None:
    if SENTINEL.exists():
        os.remove(SENTINEL)


def test_pickle_payload_executes_on_load() -> None:
    """The crafted pickle runs code on load, shown by the sentinel appearing."""
    _clear_sentinel()
    blob = pickle.dumps(_CraftedPayload())
    assert not SENTINEL.exists(), "sentinel should not exist before loading"
    load_pickle(blob)
    assert SENTINEL.exists(), "unpickling the crafted payload executed its code"
    _clear_sentinel()


def test_json_path_does_not_execute_and_validates_shape() -> None:
    """The JSON path never executes code and confirms the shape is valid."""
    _clear_sentinel()
    text = json.dumps({"product_id": "P-77", "rating": 5})
    review = load_json_reviewed(text)
    # No code ran: no sentinel appeared.
    assert not SENTINEL.exists(), "loading JSON must never execute code"
    # And the shape is what we required.
    assert review["product_id"] == "P-77"
    assert review["rating"] == 5


def test_json_schema_rejects_bad_shape() -> None:
    """A JSON body with the wrong types is rejected by the schema check."""
    bad = json.dumps({"product_id": "P-77", "rating": "five"})
    raised = False
    try:
        load_json_reviewed(bad)
    except ValueError:
        raised = True
    assert raised, "rating of the wrong type must be rejected"
