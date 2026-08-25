"""Make a two-step write all-or-nothing (reliability): commit it whole or not at all.

The concept, in plain words:
    Some writes take more than one step: build the record, then attach its tags. If the
    process is interrupted between the two steps, a naive store is left holding a half-
    written record: a row with no tags, or a shape later code cannot trust. The fix is
    to prepare the whole record off to the side and publish it into the store in a
    single final step. An interruption before that step leaves the store empty; the
    record only appears once it is complete. You never see a half, and you never see
    two.

Why a fresher should care:
    Crashes do not wait for a tidy moment. A commit that flips from "nothing" to "the
    whole record" in one move means any interruption leaves the store in a state your
    code can handle.

What this demo shows:
    An atomic_append that builds the full record first and publishes it last. The test
    runs it with an interruption injected between the two build steps and asserts the
    store is either empty or holds exactly one complete record: never a partial, never a
    duplicate.

Run:  poetry run pytest demo_crash_in_the_middle.py -v
"""

from __future__ import annotations

import contextlib
from typing import Any


class Interrupted(Exception):
    """Stands in for a crash: raised between build steps to model an interruption."""


def atomic_append(
    store: list[dict[str, Any]],
    product_id: str,
    tags: list[str],
    interrupt_before_publish: bool = False,
) -> None:
    """Append one complete record to the store, all-or-nothing.

    We assemble the whole record in a local variable first. The store is only
    touched by the single append at the end. If the interruption fires before that
    append, the store is never modified, so it stays whole. The append itself is one
    indivisible operation.
    """
    # Step 1: build the base record off to the side, not in the store yet.
    record: dict[str, Any] = {"product_id": product_id, "tags": []}

    if interrupt_before_publish:
        # A crash lands here, after building but before publishing. The store is
        # untouched.
        raise Interrupted("process died before publish")

    # Step 2: finish the record (still off to the side).
    record["tags"] = list(tags)

    # Publish: one append flips the store from "without" to "with the whole record".
    store.append(record)


def test_interruption_leaves_store_whole() -> None:
    store: list[dict[str, Any]] = []

    # The write is interrupted before publish, so the store must stay empty
    # (zero records).
    with contextlib.suppress(Interrupted):
        atomic_append(store, "P-77", [], interrupt_before_publish=True)
    assert len(store) == 0  # never a half-written record

    # A clean write publishes exactly one complete record.
    atomic_append(store, "P-77", ["battery", "value"])
    assert len(store) == 1  # never two
    assert store[0] == {"product_id": "P-77", "tags": ["battery", "value"]}

    # The invariant across both paths: the store holds 0 or 1 records, and any
    # record is whole.
    assert len(store) in (0, 1)
    for record in store:
        assert record["product_id"] and isinstance(record["tags"], list)
