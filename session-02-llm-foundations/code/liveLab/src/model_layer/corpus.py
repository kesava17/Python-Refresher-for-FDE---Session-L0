"""Load the shared help corpus and golden question set.

These two files are the backbone of the whole Prototype phase. They are created here,
in Session 2, and reused by every later session: prompt tests, RAG grounding, the eval
harness, and the assembled PoC all point back to them.
"""

from __future__ import annotations

import csv
import json
import os

_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_corpus() -> list[dict]:
    """The Sunrise help articles: [{doc_id, title, source, topic, body}, ...]."""
    with open(os.path.join(_DATA, "help_corpus.json"), encoding="utf-8") as fh:
        return json.load(fh)


def load_golden() -> list[dict]:
    """The golden question set: labelled questions with expected docs and escalation."""
    rows: list[dict] = []
    with open(os.path.join(_DATA, "golden_questions.csv"), newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["expected_doc_ids"] = [d for d in row.get("expected_doc_ids", "").split(";") if d]
            row["should_escalate"] = row.get("should_escalate", "").strip().lower() == "true"
            rows.append(row)
    return rows
