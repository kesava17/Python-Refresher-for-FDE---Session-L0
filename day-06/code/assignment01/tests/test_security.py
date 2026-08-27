"""Security-layer tests: object-level authorization, mass assignment, masking, secret scan.

These prove the four security behaviors added on top of the dependability layer, plus the
secret scanner. The earlier tests keep passing unchanged, so no existing behavior regressed.
"""

from __future__ import annotations

import importlib.util
import logging
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from telemetry_insight.api import create_app
from telemetry_insight.security import mask_email

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


class _CaptureHandler(logging.Handler):
    """A logging handler that keeps every formatted message, so a test can inspect the logs.

    The package logger does not propagate to the root logger, so pytest's caplog does not see
    its records. Attaching this handler directly to the package logger captures them instead.
    """

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def test_bola_owner_gets_200_other_caller_gets_404() -> None:
    client = _client()
    # Caller A ingests a reading. The owner is taken from the X-User-Id header.
    created = client.post(
        "/v1/readings",
        json={"device_id": "D1", "value": 20.5},
        headers={"X-User-Id": "userA"},
    )
    assert created.status_code == 201
    reading_id = created.json()["id"]

    # The owner (caller A) can read their own reading.
    owner_view = client.get(
        f"/v1/readings/{reading_id}", headers={"X-User-Id": "userA"}
    )
    assert owner_view.status_code == 200
    assert owner_view.json()["owner_id"] == "userA"

    # Caller B, who does not own it, gets a 404, not a 403, so the id is not confirmed to exist.
    other_view = client.get(
        f"/v1/readings/{reading_id}", headers={"X-User-Id": "userB"}
    )
    assert other_view.status_code == 404


def test_mass_assignment_ignores_body_owner_and_status() -> None:
    client = _client()
    # The body tries to set owner_id and a status flag. Neither is bound by the contract, so
    # both are dropped, and the owner is set from the caller header instead.
    created = client.post(
        "/v1/readings",
        json={
            "device_id": "D1",
            "value": 20.5,
            "owner_id": "attacker",
            "status": "admin",
        },
        headers={"X-User-Id": "userA"},
    )
    assert created.status_code == 201
    reading_id = created.json()["id"]

    # The real owner is the caller, not the "attacker" value from the body: if the body had
    # won, caller A would be denied here.
    view = client.get(f"/v1/readings/{reading_id}", headers={"X-User-Id": "userA"})
    assert view.status_code == 200
    body = view.json()
    assert body["owner_id"] == "userA"
    # The server-controlled flag from the body never became part of the record.
    assert "status" not in body


def test_pii_contact_is_masked_in_logs() -> None:
    logger = logging.getLogger("telemetry_insight")
    capture = _CaptureHandler()
    logger.addHandler(capture)
    try:
        client = _client()
        raw_email = "alice@example.com"
        resp = client.post(
            "/v1/readings",
            json={"device_id": "D1", "value": 20.5, "contact_email": raw_email},
            headers={"X-User-Id": "userA"},
        )
        assert resp.status_code == 201
    finally:
        logger.removeHandler(capture)

    joined = "\n".join(capture.messages)
    # The raw contact never reaches any log line.
    assert raw_email not in joined
    # The masked form is present instead.
    assert mask_email(raw_email) in joined
    assert mask_email(raw_email) == "a****@example.com"


def test_secret_scan_reports_zero_findings_over_src() -> None:
    # The real source must contain no hard-coded secret, so the scanner exits 0.
    script = _PROJECT_ROOT / "scripts" / "secret_scan.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_secret_scan_detects_a_planted_secret(tmp_path: Path) -> None:
    # A negative control: the scanner must actually catch a hard-coded secret when there is one.
    planted = tmp_path / "leak.py"
    planted.write_text('password = "hunter2-not-a-real-secret"\n', encoding="utf-8")

    script = _PROJECT_ROOT / "scripts" / "secret_scan.py"
    spec = importlib.util.spec_from_file_location("secret_scan", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    findings = module.find_secrets(tmp_path)
    assert len(findings) == 1
