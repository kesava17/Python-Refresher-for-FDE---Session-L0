"""Security helpers for the API (the secure topic): caller identity and PII masking.

This module holds the small, reusable pieces the API uses to enforce security. None of it is
heavy: caller identity is read from a header, and masking uses plain string work. The teaching
point is the shape of the checks, not any cryptography, so the standard library is enough.
"""

from __future__ import annotations


def caller_id_from_header(x_user_id: str | None) -> str:
    """Resolve the verified caller identity for the request.

    In production the caller identity comes from a validated OAuth or JWT bearer token that an
    auth layer verifies before the request reaches this handler. That verification is out of
    scope for this lesson, so here we read a pre-verified user id from the X-User-Id header and
    focus on the authorization check itself.

    A missing identity is treated as an anonymous caller so the carried-forward tests keep
    working. A real service would reject an unauthenticated request with 401 instead.
    """
    return x_user_id or "anonymous"


def mask_email(email: str) -> str:
    """Turn "alice@example.com" into "a***@example.com" for safe logging.

    A log line should be able to say which account was involved without recording the raw
    address, so personal data never lands in the logs. The first character of the local part is
    kept as a hint, the rest is hidden, and the domain is preserved for routing questions. A
    value that is not an email is fully masked.
    """
    local, separator, domain = email.partition("@")
    if not separator or not local:
        return "***"
    return f"{local[0]}***@{domain}"


def mask_identifier(value: str) -> str:
    """Reduce a caller id to a non-identifying hint for a security log line."""
    if not value:
        return "***"
    return f"{value[0]}***"
