"""Shared API and event contracts for the reviews system.

In a full multi-repo setup each service would keep its own copy of the contract it depends
on. Here one small package holds them, so the lab stays readable and a contract change is
visible to both sides at once.
"""

from contracts.review import Aggregate, ReviewCreated, ReviewIn, ReviewReceived

__all__ = ["Aggregate", "ReviewCreated", "ReviewIn", "ReviewReceived"]
