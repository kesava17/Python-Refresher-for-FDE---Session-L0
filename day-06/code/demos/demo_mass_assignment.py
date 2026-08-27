"""Mass assignment (security): bind only the fields the client is allowed to set.

The concept, in plain words:
    A convenient pattern is to take the whole request body and copy every field onto
    your record in one line. It is easy, and it is a trap. Some fields are the server's
    to decide, not the client's: is_approved, owner_id, role, is_admin. If you bind the
    whole body, a crafted request can smuggle those fields in and set them. The fix is
    an allowlist: name the exact fields a client may set, and copy only those.
    Everything else the server fills in itself.

Why a fresher should care:
    This is how a normal user quietly makes themselves an admin, or approves their own
    content. The dangerous code looks harmless ("just save what they sent"). Deciding on
    paper which fields the client owns, and binding only those, is the whole defense.

What this demo shows:
    A Review with server-controlled fields (is_approved, owner_id). Binding the entire
    body lets a crafted body flip is_approved to True. Allowlist binding ignores the
    smuggled fields, so the review stays unapproved and owned by the real caller.

Run:  poetry run python demo_mass_assignment.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Review:
    product_id: str = ""
    rating: int = 0
    # Server-controlled. A client must never set these directly.
    is_approved: bool = False
    owner_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


# The client is allowed to set exactly these fields, and nothing else.
CLIENT_SETTABLE = ("product_id", "rating")


def bind_whole_body(body: dict[str, Any], caller_id: str) -> Review:
    """UNSAFE: copy every field from the body, trusting whatever the client sent."""
    review = Review(owner_id=caller_id)
    for key, value in body.items():
        # Setting any field named in the body, including is_approved. This is the bug.
        setattr(review, key, value)
    return review


def bind_allowlist(body: dict[str, Any], caller_id: str) -> Review:
    """SAFE: copy only allowlisted fields; the server sets the rest itself."""
    review = Review(owner_id=caller_id)  # owner comes from the session, not the body
    for key in CLIENT_SETTABLE:
        if key in body:
            setattr(review, key, body[key])
    return review


def main() -> None:
    # A crafted body: the two real fields, plus two smuggled server-owned fields.
    crafted_body: dict[str, Any] = {
        "product_id": "P-77",
        "rating": 5,
        "is_approved": True,  # smuggled: the client is trying to approve its own review
        "owner_id": "user-A",  # smuggled: trying to write the review under someone else
    }
    caller_id = "user-B"

    unsafe = bind_whole_body(crafted_body, caller_id)
    print(
        "whole-body bind -> "
        f"is_approved={unsafe.is_approved}, owner_id={unsafe.owner_id!r}"
    )
    print("  the crafted body approved itself and set a false owner")

    safe = bind_allowlist(crafted_body, caller_id)
    print(
        "allowlist bind  -> "
        f"is_approved={safe.is_approved}, owner_id={safe.owner_id!r}"
    )
    print("  smuggled fields ignored: stays unapproved and owned by the real caller")


if __name__ == "__main__":
    main()
