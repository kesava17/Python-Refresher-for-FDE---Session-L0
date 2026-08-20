"""Dict versus dataclass (Level 1.3): give recurring data an explicit shape.

The concept, in plain words:
    A dict is perfect for a quick, local bag of values. But once the same dict is passed through
    several functions, each one has to guess its keys, and a typo becomes a runtime surprise or,
    worse, silent junk. A dataclass gives the data a named shape, so the fields are explicit and a
    wrong name is caught, by the type checker before you run, and by a clear error if you do.

Why a fresher should care:
    "What keys does this dict have?" is a question you should never have to answer by reading five
    functions. A dataclass answers it in one place, which is exactly what keeps code maintainable.

What this demo shows:
    Reading a mistyped key from a dict raises KeyError only at runtime, and writing a mistyped key
    is accepted silently. The same data as a dataclass has one declared shape.

Run:  poetry run python demo_dict_vs_dataclass.py
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Review:
    product_id: str
    rating: int


def main() -> None:
    # A dict has no fixed shape. A mistyped key on READ is only caught when the code runs.
    as_dict = {"product_id": "P1", "rating": 5}
    try:
        print(as_dict["ratng"])  # typo: KeyError at runtime
    except KeyError as exc:
        print("dict typo on read, found only at runtime:", exc)

    # A mistyped key on WRITE is worse: the dict accepts it silently and the data drifts.
    as_dict["ratng"] = 4
    print("dict silently accepted a junk key:", "ratng" in as_dict)  # True

    # A dataclass has a declared shape: the fields are named once and are explicit everywhere.
    review = Review(product_id="P1", rating=5)
    print("dataclass access is explicit:", review.product_id, review.rating)
    # Note: writing review.ratng would be flagged by mypy before the program ever runs.


if __name__ == "__main__":
    main()
