"""Webhook signature check (security): prove the sender knows the shared secret.

The concept, in plain words:
    A webhook is someone else's server POSTing to yours. Anyone on the internet can POST
    to that URL, so "it arrived" is not "it is genuine". The sender and you share a
    secret. The sender computes an HMAC-SHA256 over the exact raw body using that secret
    and puts the result in a header. You recompute the HMAC over the raw bytes you
    received and compare. If they match, the sender knew the secret and the body was not
    changed in flight. Two details matter: sign the RAW body (not a re-serialized
    version, which can differ byte for byte), and compare with hmac.compare_digest,
    which takes the same time whether the first byte or the last byte is wrong, so
    attackers cannot guess the signature one byte at a time by measuring response times.

Why a fresher should care:
    Payment providers, git hosts, and messaging platforms all send signed webhooks, and
    "trusting" an unsigned one lets anyone forge events (a fake "payment succeeded").
    The verify step is a few lines, and getting the compare wrong quietly reopens the
    hole.

What this demo shows:
    A signed request built with the shared secret verifies as genuine. A forged request
    with the wrong signature is rejected. The tests prove both outcomes.

Run:  poetry run pytest demo_hmac_webhook.py -v
"""

from __future__ import annotations

import hashlib
import hmac

# The secret both sides hold. In production it comes from config/secrets, not source.
SHARED_SECRET = b"whsec_demo_shared_secret"


def sign(body: bytes, secret: bytes = SHARED_SECRET) -> str:
    """Compute the HMAC-SHA256 signature over the raw body, as hex."""
    return hmac.new(secret, body, hashlib.sha256).hexdigest()


def verify(body: bytes, signature: str, secret: bytes = SHARED_SECRET) -> bool:
    """Recompute the signature and compare in constant time."""
    expected = sign(body, secret)
    # compare_digest avoids leaking, through timing, how many bytes matched.
    return hmac.compare_digest(expected, signature)


def test_genuine_signature_is_accepted() -> None:
    """A body signed with the shared secret verifies as genuine."""
    body = b'{"event":"review.created","id":"R-1"}'
    signature = sign(body)  # the real sender computes this with the same secret
    assert verify(body, signature) is True


def test_forged_signature_is_rejected() -> None:
    """A body with a made-up signature is rejected."""
    body = b'{"event":"review.created","id":"R-1"}'
    forged = "0" * 64  # attacker does not know the secret, so guesses
    assert verify(body, forged) is False


def test_tampered_body_is_rejected() -> None:
    """A signature that was valid for the original body fails once the body changes."""
    original = b'{"event":"payout","amount":10}'
    signature = sign(original)
    tampered = b'{"event":"payout","amount":1000000}'  # attacker inflates the amount
    assert verify(tampered, signature) is False
