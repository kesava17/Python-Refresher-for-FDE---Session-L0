"""Security logging without leaking PII (security): log the event, mask the person.

The concept, in plain words:
    Security logs need to be useful for an investigation and safe to keep. Useful means
    structured: an event name, a trace id, the resource touched, so you can search and
    correlate. Safe means the log must not become its own data leak. Logs get shipped to
    third-party systems, indexed, and read by many people, so raw personal data (a full
    email, a phone number, a card) must never be written into them. The fix is a masking
    helper applied at the moment you log: keep enough to recognize a value
    ("p***@example.com") without storing the value itself.

Why a fresher should care:
    It is easy to "just log the whole request to debug it" and thereby copy every user's
    email into a log index that is far less protected than your database. Masking at the
    log boundary is a habit that keeps one useful log line from turning into a second
    breach.

What this demo shows:
    A structured JSON security event with a fixed trace_id and the resource touched. The
    reviewer's email is passed through a masking helper, and the output is checked to
    confirm the raw address never appears in the emitted line.

Run:  poetry run python demo_security_logging.py
"""

from __future__ import annotations

import json


def mask_email(email: str) -> str:
    """Keep the first character and the domain; hide the rest of the local part."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if not local:
        return "***@" + domain
    return local[0] + "***@" + domain


def security_event(event: str, trace_id: str, resource: str, actor_email: str) -> str:
    """Return one structured JSON security line with the actor's email masked."""
    record = {
        "level": "security",
        "event": event,
        "trace_id": trace_id,  # fixed here so the output is identical every run
        "resource": resource,
        "actor": mask_email(actor_email),  # masked at the boundary, never raw
    }
    return json.dumps(record)


def main() -> None:
    raw_email = "priya.reviewer@example.com"
    line = security_event(
        event="review.access_denied",
        trace_id="9f2a-fixed-trace",
        resource="review:R-1",
        actor_email=raw_email,
    )
    print(line)

    # Prove the raw address never made it into the emitted line.
    print(f"\nraw email present in the log line? {raw_email in line}")
    print(f"masked form shown instead:         {mask_email(raw_email)}")


if __name__ == "__main__":
    main()
