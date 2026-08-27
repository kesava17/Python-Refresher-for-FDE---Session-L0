"""The security layer (Assignment 2, Secure topic): the small, testable pieces of hardening.

Financial records are the most sensitive data in this course: money in rupees, stored as
paise. So this module concentrates the security habits an on-call engineer must be able to
trust. It masks the account identifier before anything reaches a log, and it emits one
structured security event for an authorization denial or a validation rejection. Every
function here uses only the standard library, so a learner can read each piece end to end.

The wider hardening (object-level authorization, mass-assignment protection, and the hardened
container) lives next to the code it protects: the authorization checks are in api.py where the
routes are, and the container rules are in the Dockerfile. This module holds the shared helpers
those places call.
"""

from __future__ import annotations

import json
import logging

# --- Masking sensitive identifiers before they reach a log --------------------------


def mask_account(account_id: str) -> str:
    """Return the account id with only the last four characters shown, for example ****6789.

    A log line is read by many people and is often shipped to a third-party log tool, so a full
    account identifier must never appear in it. We keep only the last four characters, which is
    enough for a human to correlate a support ticket, and hide the rest behind four stars. A very
    short id is masked completely, so we never accidentally reveal most of it.
    """
    if len(account_id) <= 4:
        return "****"
    return "****" + account_id[-4:]


# --- One structured security event per notable event --------------------------------


def log_security_event(
    logger: logging.Logger,
    event: str,
    trace_id: str,
    resource: str,
    account: str = "",
) -> None:
    """Emit one JSON line describing a security event, carrying no secret or raw sensitive data.

    A security event (an authorization denial, a validation rejection) is worth its own line so a
    log tool can alert on it. The line carries the event name, the trace id that ties it to the
    request, the resource that was touched, and the masked account. It never carries a token, a
    signature, a password, or a full account identifier, so shipping the log elsewhere leaks
    nothing. The amount is left out on purpose, so an account and a value are never logged
    together in the clear.
    """
    payload = {
        "event": event,
        "trace_id": trace_id,
        "resource": resource,
        "account": mask_account(account) if account else "",
    }
    # A security event is logged at WARNING so it stands out from the routine INFO request lines.
    logger.warning(json.dumps(payload))
