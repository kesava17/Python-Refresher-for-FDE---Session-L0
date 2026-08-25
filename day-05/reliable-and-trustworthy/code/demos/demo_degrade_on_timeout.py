"""Degrade on a dependency timeout (reliability): a partial page beats a broken one.

The concept, in plain words:
    A review page might call an "insight" service to add extra detail. That service can
    be slow or down. If your page dies whenever the extra call dies, one shaky
    dependency takes the whole page with it. The safer design is to try the call with a
    timeout and, when it fails, return the review without the extra detail. The reader
    still sees the review.

Why a fresher should care:
    Enrichment is a nice-to-have; the review itself is the must-have. Wrapping the
    optional call so a failure returns a plain result keeps the core feature working
    while the dependency heals.

What this demo shows:
    enrich_or_degrade calls the insight service with a timeout. The test injects a
    client that always raises httpx.TimeoutException, then asserts the result still
    carries the original product_id and has enriched set to False, proving the page
    degrades cleanly.

Run:  poetry run pytest demo_degrade_on_timeout.py -v
"""

from __future__ import annotations

import asyncio
from typing import Any, Protocol

import httpx


class InsightClient(Protocol):
    """The slice of an async HTTP client we depend on: just a post call."""

    async def post(self, url: str, json: dict[str, Any]) -> httpx.Response: ...


async def enrich_or_degrade(
    review: dict[str, Any], client: InsightClient
) -> dict[str, Any]:
    """Add an insight to the review, or return it unenriched if the call fails.

    We try the optional insight call with a short timeout. Any httpx error (a
    timeout is the common one) drops us into the fallback, which returns the
    original review plus flags marking that the enrichment did not happen. The
    core review data is never lost.
    """
    try:
        response = await client.post(
            "https://insight.example/v1/insight", json={"review": review}
        )
        response.raise_for_status()
        insight = response.json()["insight"]
    except httpx.HTTPError:
        # TimeoutException subclasses HTTPError, so slow and broken both land here.
        return {**review, "insight": None, "enriched": False}
    return {**review, "insight": insight, "enriched": True}


class _AlwaysTimeout:
    """A stand-in client whose post always times out, to test the fallback path."""

    async def post(self, url: str, json: dict[str, Any]) -> httpx.Response:
        raise httpx.TimeoutException("insight service too slow")


def test_degrades_when_insight_times_out() -> None:
    # A sync test that drives the async function with asyncio.run, needing no
    # extra plugin.
    review = {"product_id": "P-77", "text": "solid battery life", "stars": 4}
    result = asyncio.run(enrich_or_degrade(review, _AlwaysTimeout()))

    # The optional enrichment failed, so the flag must say so.
    assert result["enriched"] is False
    assert result["insight"] is None
    # The core review data must survive the degraded path untouched.
    assert result["product_id"] == "P-77"
    assert result["stars"] == 4
