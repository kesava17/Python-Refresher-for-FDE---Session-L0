"""Security tests (the secure topic): object-level authorization, mass assignment, PII, secrets.

These prove the hardening added on top of the dependable service. They use the FastAPI
TestClient for the HTTP surface, capture the structured logs with a plain logging handler (the
service logger does not propagate, so we attach our own), and load the CI secret scanner from its
script path to check the real source is clean.
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.testclient import TestClient

from reviews_insight.api import create_app
from reviews_insight.security import mask_email, mask_identifier

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _client() -> TestClient:
    # A fresh app (and a fresh in-memory store) per test, so the tests do not affect each other.
    return TestClient(create_app())


def _submit(client: TestClient, product_id: str, rating: int, user: str) -> None:
    # A caller identity is carried in X-User-Id; in production it comes from a verified token.
    resp = client.post(
        "/v1/reviews",
        json={"product_id": product_id, "rating": rating},
        headers={"X-User-Id": user},
    )
    assert resp.status_code == 201


def _first_review_id(client: TestClient) -> str:
    # The listing exposes the review id (but never the owner), which is how a caller learns an id.
    items = client.get("/v1/reviews").json()["items"]
    return str(items[0]["review_id"])


@pytest.fixture
def captured_logs() -> Iterator[list[str]]:
    # The service logger has propagate=False and its own stdout handler, so caplog cannot see it.
    # Attach a throwaway handler that records each formatted message, then remove it afterwards.
    records: list[str] = []
    logger = logging.getLogger("reviews_insight")

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record.getMessage())

    handler = _Capture()
    logger.addHandler(handler)
    try:
        yield records
    finally:
        logger.removeHandler(handler)


def test_bola_owner_can_read_other_cannot() -> None:
    # Caller A creates a review. A can read it (200); caller B cannot and gets 404, not 403, so
    # B cannot even confirm the id exists. This is the object-level authorization fix.
    client = _client()
    _submit(client, "P1", 5, user="user-a")
    review_id = _first_review_id(client)

    owner = client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "user-a"})
    assert owner.status_code == 200
    assert owner.json()["review_id"] == review_id

    other = client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "user-b"})
    assert other.status_code == 404


def test_bola_denial_emits_security_event(captured_logs: list[str]) -> None:
    # An authorization denial must be recorded as a structured security event, carrying the
    # resource id and the masked caller, with no raw identity in it.
    client = _client()
    _submit(client, "P1", 5, user="user-a")
    review_id = _first_review_id(client)

    client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "user-b"})

    denials = [line for line in captured_logs if "authz_denied" in line]
    assert denials, "expected an authz_denied security event"
    assert review_id in denials[-1]
    assert mask_identifier("user-b") in denials[-1]
    assert "user-b" not in denials[-1]  # the raw caller id is never logged


def test_mass_assignment_cannot_set_server_fields() -> None:
    # The body tries to smuggle owner_id and is_flagged. Neither may take effect: the stored
    # review must have the server-assigned owner (from X-User-Id) and the default flags.
    client = _client()
    resp = client.post(
        "/v1/reviews",
        json={
            "product_id": "P1",
            "rating": 5,
            "owner_id": "attacker",
            "is_flagged": True,
            "enriched": True,
        },
        headers={"X-User-Id": "real-owner"},
    )
    assert resp.status_code == 201

    review_id = _first_review_id(client)
    # The real owner can read it; the smuggled "attacker" owner cannot, which proves owner_id was
    # taken from the verified caller and not from the body.
    assert client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "real-owner"}).status_code == 200
    assert client.get(f"/v1/reviews/{review_id}", headers={"X-User-Id": "attacker"}).status_code == 404


def test_pii_email_is_masked_in_logs_and_raw_never_appears(captured_logs: list[str]) -> None:
    # Submitting with a reviewer_email must log only the masked form; the raw address must not
    # appear in any log line.
    client = _client()
    raw_email = "alice@example.com"
    resp = client.post(
        "/v1/reviews",
        json={"product_id": "P1", "rating": 5, "reviewer_email": raw_email},
        headers={"X-User-Id": "user-a"},
    )
    assert resp.status_code == 201

    masked = mask_email(raw_email)
    assert masked == "a***@example.com"
    events = [line for line in captured_logs if "review_received" in line]
    assert events, "expected a review_received security event"
    assert any(masked in line for line in events)
    assert all(raw_email not in line for line in captured_logs)  # the raw email never appears


def test_validation_rejection_emits_security_event(captured_logs: list[str]) -> None:
    # A schema rejection is a security event too. A bad rating is refused with 422 and recorded.
    client = _client()
    resp = client.post("/v1/reviews", json={"product_id": "P1", "rating": 99})
    assert resp.status_code == 422
    assert any("validation_rejected" in line for line in captured_logs)


def _load_secret_scan() -> ModuleType:
    # scripts/ is not an importable package, so load the scanner from its file path.
    path = _PROJECT_ROOT / "scripts" / "secret_scan.py"
    spec = importlib.util.spec_from_file_location("secret_scan", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # register before exec so the frozen dataclass resolves
    spec.loader.exec_module(module)
    return module


def test_secret_scan_finds_nothing_in_real_source() -> None:
    # The CI proof: running the scanner over src/ reports zero findings.
    scanner = _load_secret_scan()
    findings = scanner.scan_source()
    assert findings == []


def test_secret_scan_detects_a_planted_secret() -> None:
    # The scanner is only convincing if it can catch a real one, so feed it a hard-coded secret.
    scanner = _load_secret_scan()
    planted = 'aws_secret_access_key = "AbcdEfgh1234567890Xyz"'
    assert scanner.scan_text(planted)
