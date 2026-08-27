"""Secure topic tests: object-level authorization, mass assignment, masking, and the secret scan.

Each test names the weakness it defends against. Together they show that the security layer holds:
one caller cannot read another caller's transaction, a crafted body cannot set server-only fields,
a full account identifier never reaches a log, and no secret is hard-coded in the source tree.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from transactions_insight.api import create_app

# The account id is a distinctive value, so the masking test can prove the full form is absent from
# the log while its masked form (****3210) is present.
_FULL_ACCOUNT = "9876543210"


def _client() -> TestClient:
    # A fresh app (and a fresh store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _create(client: TestClient, user_id: str, **body: object) -> dict[str, object]:
    """Create a transaction as a given caller and return the response body."""
    payload = {"account_id": _FULL_ACCOUNT, "amount": 250.0, "currency": "INR"}
    payload.update(body)
    resp = client.post("/v1/transactions", json=payload, headers={"X-User-Id": user_id})
    assert resp.status_code == 201
    return resp.json()


# --- Object-level authorization (the BOLA fix) --------------------------------------


def test_owner_can_read_but_another_caller_gets_404() -> None:
    # Caller A creates a transaction. A can read it back (200), but caller B is told it does not
    # exist (404), even though the id is valid. The 404, not a 403, keeps B from learning that the
    # id is real, so ids cannot be enumerated.
    client = _client()
    created = _create(client, user_id="userA")
    transaction_id = created["id"]

    as_owner = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userA"}
    )
    assert as_owner.status_code == 200
    assert as_owner.json()["id"] == transaction_id

    as_other = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userB"}
    )
    assert as_other.status_code == 404


def test_unknown_id_also_returns_404() -> None:
    # A made-up id fails the same way as one owned by someone else, so the two cases are
    # indistinguishable to a caller.
    client = _client()
    resp = client.get("/v1/transactions/does-not-exist", headers={"X-User-Id": "userA"})
    assert resp.status_code == 404


# --- Mass-assignment protection -----------------------------------------------------


def test_body_supplied_owner_and_status_are_ignored() -> None:
    # The caller tries to set the owner and the status from the body. Both are server-controlled,
    # so both are ignored: the real owner is the caller (userLegit), and the status is the
    # server value "received", never the "approved" the body asked for.
    client = _client()
    created = _create(
        client, user_id="userLegit", owner="attacker", status="approved"
    )
    transaction_id = created["id"]

    # The status came from the server, not the body.
    assert created["status"] == "received"

    # The body-supplied owner did not take effect: the attacker it named cannot read the record.
    as_attacker = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "attacker"}
    )
    assert as_attacker.status_code == 404

    # The real owner (the caller) can read it.
    as_owner = client.get(
        f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userLegit"}
    )
    assert as_owner.status_code == 200


# --- Sensitive-data masking in logs -------------------------------------------------


def test_full_account_never_appears_in_logs_but_masked_form_does(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # A denied authorization logs a security event. That event must carry the masked account
    # (****3210) and never the full account id, so shipping the log elsewhere leaks nothing.
    client = _client()
    created = _create(client, user_id="userA")
    transaction_id = created["id"]

    with caplog.at_level(logging.WARNING, logger="transactions_insight"):
        denied = client.get(
            f"/v1/transactions/{transaction_id}", headers={"X-User-Id": "userB"}
        )
    assert denied.status_code == 404

    logged = caplog.text
    assert _FULL_ACCOUNT not in logged  # the full account id is never written in the clear
    assert "****3210" in logged  # the masked form is present, enough to correlate a ticket


# --- Secrets hygiene: the scanner finds nothing in real source ----------------------


def test_secret_scan_reports_zero_findings_over_src() -> None:
    # Run the same scanner the pipeline runs. Over the real source it must find nothing and exit 0.
    script = Path(__file__).resolve().parents[1] / "scripts" / "secret_scan.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 findings" in result.stdout
