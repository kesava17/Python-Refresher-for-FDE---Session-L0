"""Verify webhook signatures (Level 1.7): never trust a payload just because it arrived.

The concept, in plain words:
    A webhook is an HTTP call some other system makes into yours. Anyone on the internet can send
    the same shape of request, so arrival proves nothing. The sender and you share a secret. The
    sender signs the exact bytes it sends with HMAC-SHA256, and you recompute the signature over
    the bytes you received. If they match, the payload really came from the holder of the secret
    and was not tampered with.

Why a fresher should care:
    An unverified webhook endpoint is an open door: a forged "review accepted" event could drive
    real actions. Verification is a few lines, and the one detail that matters is comparing with
    hmac.compare_digest, which takes constant time and does not leak the answer through timing.

What this demo shows:
    We sign a JSON payload with a shared secret. A receiver that recomputes the signature accepts
    it. A forged signature over the same payload fails and is rejected. Both checks use
    hmac.compare_digest.

Run:  poetry run python demo_webhook_signature.py
"""

from __future__ import annotations

import hashlib
import hmac
import json

# In real life this lives in a secret store, never in the code. It is shared with the sender only.
SHARED_SECRET = b"shared-webhook-secret"


def sign(payload: bytes, secret: bytes) -> str:
    """Compute the HMAC-SHA256 signature of the exact bytes, as a hex string."""
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def verify(payload: bytes, signature: str, secret: bytes) -> bool:
    """Recompute the signature and compare in constant time, so timing leaks nothing."""
    expected = sign(payload, secret)
    return hmac.compare_digest(expected, signature)


def main() -> None:
    # The sender serializes the event and signs those exact bytes.
    event = {"event": "review.accepted", "review_id": "R-1001"}
    body = json.dumps(event).encode("utf-8")
    real_signature = sign(body, SHARED_SECRET)
    print("payload        :", event)
    print("signature      :", real_signature[:16], "...")

    # A genuine delivery: the receiver recomputes the same signature and accepts it.
    genuine_ok = verify(body, real_signature, SHARED_SECRET)
    print("genuine call   :", "accepted" if genuine_ok else "rejected")

    # A forged delivery: an attacker guesses a signature without the secret. It does not match.
    forged_signature = "0" * len(real_signature)
    forged_ok = verify(body, forged_signature, SHARED_SECRET)
    print("forged call    :", "accepted" if forged_ok else "rejected")


if __name__ == "__main__":
    main()
