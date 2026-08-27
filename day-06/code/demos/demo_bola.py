"""Broken Object Level Authorization (security): check the owner, not just the login.

The concept, in plain words:
    Almost every endpoint takes an id, like /reviews/42, and loads that object. The
    login check ("are you signed in?") is easy to remember. The object check ("is this
    YOUR review?") is easy to forget. BOLA is that forgotten check: a signed-in user
    passes another user's id and gets an object they were never allowed to see. The fix
    is one comparison on the way out: the object's owner_id must match the caller's id,
    and if it does not, the server answers 404 (not found), not 403 (forbidden).

Why a fresher should care:
    This is the number one API risk in the wild. It is not a clever exploit; it is a
    missing "if". Any handler that loads an object by id needs the owner check, every
    time, or one user can read and edit another user's data by changing a number.

Why 404 and not 403:
    A 403 ("you are not allowed") confirms the object exists, so an attacker can count
    real ids by walking the numbers. A 404 ("no such thing here") leaks nothing: the
    caller cannot tell an object they do not own apart from one that does not exist.

What this demo shows:
    A store of reviews, each with an owner_id. The broken get_review hands any review to
    any caller. The fixed get_review checks ownership and raises 404 otherwise. The
    tests prove user B is blocked on the fixed version and (the bug) reads user A's data
    on the broken version.

Run:  poetry run pytest demo_bola.py -v
"""

from __future__ import annotations

from dataclasses import dataclass


class NotFound(Exception):
    """Maps to HTTP 404. We raise this instead of 403 so ids cannot be enumerated."""


@dataclass(frozen=True)
class User:
    id: str


@dataclass(frozen=True)
class Review:
    id: str
    owner_id: str  # the user who wrote it; only they may read or edit it
    text: str


# A tiny store. Review R-1 belongs to user A, R-2 belongs to user B.
REVIEWS: dict[str, Review] = {
    "R-1": Review(id="R-1", owner_id="user-A", text="Great mixer, quiet motor."),
    "R-2": Review(id="R-2", owner_id="user-B", text="Battery drains fast."),
}


def get_review_broken(review_id: str, caller: User) -> Review:
    """BROKEN: looks up by id and returns it, never checking who is asking."""
    review = REVIEWS[review_id]
    # The owner check that belongs here is missing, so any caller gets any review.
    return review


def get_review_fixed(review_id: str, caller: User) -> Review:
    """FIXED: return the review only when the caller owns it, else raise 404."""
    review = REVIEWS.get(review_id)
    # One combined check: unknown id and not-your-id look identical from outside,
    # so an attacker cannot tell which ids are real.
    if review is None or review.owner_id != caller.id:
        raise NotFound(review_id)
    return review


def test_fixed_blocks_other_users_with_404() -> None:
    """User B asks for user A's review on the fixed handler and is denied with 404."""
    user_b = User(id="user-B")
    raised = False
    try:
        get_review_fixed("R-1", caller=user_b)
    except NotFound:
        raised = True
    assert raised, "fixed handler must deny access to a review the caller does not own"


def test_fixed_allows_the_owner() -> None:
    """The real owner still reads their own review on the fixed handler."""
    user_a = User(id="user-A")
    review = get_review_fixed("R-1", caller=user_a)
    assert review.owner_id == "user-A"


def test_fixed_missing_and_forbidden_are_indistinguishable() -> None:
    """A missing id and a not-owned id both raise 404, so ids cannot be enumerated."""
    user_b = User(id="user-B")
    errors: list[str] = []
    # R-1 exists but is not B's; R-999 does not exist. Both must look identical.
    for review_id in ("R-1", "R-999"):
        try:
            get_review_fixed(review_id, caller=user_b)
        except NotFound:
            errors.append("404")
    # Both cases produce the same 404, so B learns nothing about which ids are real.
    assert errors == ["404", "404"]


def test_broken_leaks_other_users_data() -> None:
    """The broken handler hands user A's private review to user B. This is the bug."""
    user_b = User(id="user-B")
    stolen = get_review_broken("R-1", caller=user_b)
    # The demo asserts the leak so the test suite documents exactly what is wrong.
    assert stolen.owner_id == "user-A"
    assert stolen.text == "Great mixer, quiet motor."
