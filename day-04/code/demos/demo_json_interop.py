"""JSON as the lingua franca (Day 5): a language-neutral contract on the wire.

The concept, in plain words:
    Two systems rarely share a language, but they can share JSON: plain text that every language
    can produce and parse. You serialize your object to a JSON string, that string travels across
    the wire, and the other side parses it back into its own objects. The string is the contract;
    the languages on either end do not matter.

Why a fresher should care:
    This round trip (object to string to object) is what every REST call, message queue, and config
    file is doing underneath. Seeing it in one file, with a dataclass on both ends, demystifies the
    whole idea of "talking to another service".

What this demo shows:
    A frozen Review dataclass is turned into a dict, then into a JSON string (all that ever crosses
    the wire). We parse the string back and rebuild an identical Review, proving the round trip.

Run:  poetry run python demo_json_interop.py
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Review:
    """One review as a value object. Frozen, so a parsed copy cannot drift from the original."""

    product_id: str
    rating: int


def main() -> None:
    # The object we hold in Python, before anything crosses a boundary.
    original = Review(product_id="P1", rating=4)

    # Serialize: dataclass -> plain dict -> JSON string. Only this text goes on the wire.
    wire = json.dumps(dataclasses.asdict(original))
    print("on the wire (str)   :", wire)

    # "Send" it across. Here that is just handing the same string to the other side.
    received = wire

    # Deserialize: parse the JSON back to a dict, then rebuild the dataclass from its fields.
    parsed = json.loads(received)
    restored = Review(**parsed)

    # The round trip preserved every field: what went out is what came back.
    print("restored object     :", restored)
    print("round trip matches  :", restored == original)


if __name__ == "__main__":
    main()
