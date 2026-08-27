"""Security helpers for the hardened layer.

This module holds the small, dependency-light pieces the security layer needs, all
built on the standard library:

- A masking helper for sensitive contact fields, so a raw email never reaches a log.
- A caller-identity masking helper, so we can record who was denied without leaking the
  full identity.
- A structured security-event logger that carries the trace id and the affected resource
  but no secrets and no raw personal data.

The teaching point is that logs are a real attack surface. Anything sensitive that lands
in a log line can leak, so we mask before we write, never after.
"""

from __future__ import annotations

import re

from telemetry_insight.observability import log_event

# A simple email shape. We only need to split the local part from the domain so we can mask
# the local part. This is not full email validation, just enough to mask safely.
_EMAIL_RE = re.compile(r"^([^@]+)@(.+)$")


def _mask_token(value: str) -> str:
    """Keep the first character and replace the rest with asterisks.

    An empty value becomes four asterisks, so we never return an empty string that a reader
    might mistake for "no value".
    """
    if not value:
        return "****"
    return value[0] + "*" * max(len(value) - 1, 1)


def mask_email(value: str) -> str:
    """Return a masked form of an email that is safe to log.

    We keep the first character of the local part and the whole domain, and replace the rest
    of the local part with asterisks: "alice@example.com" becomes "a****@example.com". A value
    that does not look like an email is masked whole, so an unexpected raw value never leaks.
    """
    match = _EMAIL_RE.match(value)
    if match is None:
        # Not an email shape: mask the whole value rather than risk leaking it.
        return "****"
    local, domain = match.group(1), match.group(2)
    return f"{_mask_token(local)}@{domain}"


def mask_caller(caller: str) -> str:
    """Mask a caller identity for logging, keeping only the first character."""
    return _mask_token(caller)


def log_security_event(
    event: str, trace_id: str, resource: str, caller: str, status: int
) -> None:
    """Emit one structured security event: no secrets, no raw personal data.

    The caller identity is masked before it reaches the log. The line records the event name
    (for example "authz_denied" or "validation_rejected"), the trace id that ties it to a
    single request, the affected resource, the masked caller, and a status code.
    """
    log_event(
        event,
        trace_id,
        0.0,
        status,
        resource=resource,
        caller=mask_caller(caller),
    )
