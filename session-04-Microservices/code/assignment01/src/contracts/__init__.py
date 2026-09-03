"""Shared API and event contracts for the telemetry system.

In a full multi-repo setup each service would keep its own copy of the contract it depends
on. Here one small package holds them, so the lab stays readable and a contract change is
visible to both sides at once.
"""

from contracts.reading import ReadingCreated, ReadingIn, ReadingReceived, Rollup

__all__ = ["ReadingCreated", "ReadingIn", "ReadingReceived", "Rollup"]
