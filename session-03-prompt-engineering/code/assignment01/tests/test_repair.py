"""Assignment 1 target tests. Both FAIL on the starter; make them pass.

1. Every held question must produce a valid Answer (repair the flaky return prompt).
2. Every Answer must carry a topic in the allowed set (add the new field).
"""

from __future__ import annotations

import csv
import os

from prompt_layer.answerer import respond

_DATA = os.path.join(os.path.dirname(__file__), "..", "data")
ALLOWED_TOPICS = {"order", "return", "warranty", "out_of_scope"}


def _held() -> list[dict]:
    """Load the held test set of labelled questions."""
    with open(os.path.join(_DATA, "prompt_tests.csv"), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_all_held_questions_return_a_valid_answer() -> None:
    """Fails on the starter: the return prompt returns an uncited, non-escalated answer."""
    for row in _held():
        respond(row["question"])  # must not raise a ValidationError


def test_answer_carries_a_topic_in_the_allowed_set() -> None:
    """Fails on the starter: the Answer has no topic field yet."""
    result = respond("Where is my order SE-100234?")
    assert result.topic in ALLOWED_TOPICS
