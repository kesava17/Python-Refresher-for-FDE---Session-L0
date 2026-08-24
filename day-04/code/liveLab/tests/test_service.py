"""Day 3 proof: the service works with any source, and swapping the source needs no logic change."""

from __future__ import annotations

from pathlib import Path

from reviews_insight.service import SummaryService
from reviews_insight.sources import CsvReviewSource, InMemoryReviewSource

ROWS = [
    {"product_id": "P1", "rating": "5"},
    {"product_id": "P1", "rating": "4"},
    {"product_id": "P2", "rating": "3"},
    {"product_id": "P3", "rating": "11"},  # bad: rating out of range
    {"product_id": "", "rating": "2"},  # bad: empty product id
]
CSV_TEXT = "product_id,rating,text\nP1,5,great\nP1,4,good\nP2,3,ok\nP3,11,bad\n,2,bad\n"


def test_service_with_in_memory_source() -> None:
    # No file, no disk: the in-memory source satisfies the same ReviewSource contract.
    service = SummaryService(InMemoryReviewSource(ROWS))
    assert service.summarize() == {"reviews": 3, "products": 2, "rejected": 2}


def test_swapping_source_keeps_the_same_result(tmp_path: Path) -> None:
    # The same data reaches the service two ways: from a CSV file, and from memory.
    sample = tmp_path / "sample.csv"
    sample.write_text(CSV_TEXT, encoding="utf-8")

    from_file = SummaryService(CsvReviewSource(str(sample))).summarize()
    from_memory = SummaryService(InMemoryReviewSource(ROWS)).summarize()

    # The seam works: the service logic was untouched; only the injected source differed.
    assert from_file == from_memory == {"reviews": 3, "products": 2, "rejected": 2}
