"""The N+1 problem (Level 1.6): one list read plus a lookup per row, and the batching fix.

The concept, in plain words:
    You fetch a list of reviews, then, for each review, you fetch its author. Five reviews means
    one list read and five author reads: six trips. Grow the list to a thousand and you make a
    thousand and one trips. That is the N+1 problem. The fix is to collect all the author ids first
    and fetch them in one batched call, turning N trips into one.

Why a fresher should care:
    N+1 is the most common hidden performance bug in data-backed APIs, and it never shows up on
    small test data. Counting the calls makes it visible. The batching idea here is exactly what a
    DataLoader does for you in a real stack.

What this demo shows:
    A fake author store wrapped in a counter. A naive resolver over five reviews lands on six calls
    (1 list + 5 lookups). A batched resolver collects the author ids and does one list read plus one
    batched lookup: two calls. Same answers, far fewer trips.

Run:  poetry run python demo_n_plus_one.py
"""

from __future__ import annotations


class AuthorStore:
    """A stand-in for a database. Every read goes through here, and here we count the reads."""

    def __init__(self) -> None:
        self._authors = {
            "A1": "Divya",
            "A2": "Rahul",
            "A3": "Meera",
        }
        self.calls = 0  # how many times the store was touched, our stand-in for round trips

    def get_one(self, author_id: str) -> str:
        # One lookup, one trip.
        self.calls += 1
        return self._authors[author_id]

    def get_many(self, author_ids: list[str]) -> dict[str, str]:
        # One batched lookup for many ids, still one trip.
        self.calls += 1
        return {aid: self._authors[aid] for aid in author_ids}


# Five reviews, each pointing at an author id. Some authors are shared across reviews.
REVIEWS = [
    {"review_id": "R1", "author_id": "A1"},
    {"review_id": "R2", "author_id": "A2"},
    {"review_id": "R3", "author_id": "A1"},
    {"review_id": "R4", "author_id": "A3"},
    {"review_id": "R5", "author_id": "A2"},
]


def resolve_naive(store: AuthorStore) -> list[str]:
    """One list read, then one author lookup per review: the N+1 shape."""
    # The list read is the "+1"; imagine it as the query that fetched REVIEWS.
    store.calls += 1
    names = []
    for review in REVIEWS:
        # Each review triggers its own author trip. Five reviews, five trips.
        names.append(store.get_one(str(review["author_id"])))
    return names


def resolve_batched(store: AuthorStore) -> list[str]:
    """One list read, then one batched lookup for every author at once: two trips total."""
    # The same list read counts as one trip.
    store.calls += 1
    # Collect the ids first, then fetch them all in a single call.
    ids = [str(review["author_id"]) for review in REVIEWS]
    authors = store.get_many(ids)
    return [authors[i] for i in ids]


def main() -> None:
    naive_store = AuthorStore()
    naive_names = resolve_naive(naive_store)
    print("naive names   :", naive_names)
    print("naive calls   :", naive_store.calls, "(1 list read + 5 author lookups)")

    batched_store = AuthorStore()
    batched_names = resolve_batched(batched_store)
    print("batched names :", batched_names)
    print("batched calls :", batched_store.calls, "(1 list read + 1 batched lookup)")

    # Same answers, fewer trips: that is the whole point of batching.
    print("same result   :", naive_names == batched_names)


if __name__ == "__main__":
    main()
