"""Gate a rollout on a readiness check (reliability): a bad build never stays live.

The concept, in plain words:
    Shipping a new version should not be a leap of faith. You deploy the new version,
    run a readiness check against it (can it serve health, does a smoke test pass), and
    only then send real traffic its way. If the check fails, the gate does not promote
    it: traffic stays on, or rolls back to, the last known-good version. The bad build
    is deployed but never live, so users keep hitting a version that works while you
    investigate.

Why a fresher should care:
    Every version looks fine until it meets real traffic. A readiness gate makes
    "promote" conditional on proof, so a broken release is caught by a check instead of
    by your users.

What this demo shows:
    v1 is live. We roll out v2 and run its readiness check, which fails on purpose. The
    gate refuses to promote v2 and keeps v1 serving. We print the sequence and confirm
    the live version is still v1, so the bad build never took traffic.

Run:  poetry run python demo_rollback_gate.py
"""

from __future__ import annotations


def readiness_check(version: str) -> bool:
    """Return whether a version is ready. v2 fails here, standing in for failure."""
    # In real life this hits a health endpoint and a smoke test. We hard-code
    # the outcome:
    # v2 is not ready (it would error under traffic), everything else is fine.
    return version != "v2"


def deploy_with_gate(live_version: str, candidate: str) -> str:
    """Roll out a candidate behind a readiness gate; return the live version.

    We only promote the candidate if its readiness check passes. On failure we
    roll traffic back to the version already live, so the live pointer never
    lands on a build that failed its check.
    """
    print(f"rollout {candidate}")
    if readiness_check(candidate):
        print(f"  readiness PASS -> promote {candidate}")
        return candidate
    # The check failed, so the gate keeps the known-good version live.
    print(f"  readiness FAIL -> auto rollback to {live_version}")
    return live_version


def main() -> None:
    live = "v1"  # the known-good version currently serving
    print(f"currently live: {live}")

    live_after = deploy_with_gate(live_version=live, candidate="v2")

    print(f"\nsequence: rollout v2 -> readiness FAIL -> auto rollback to {live_after}")
    print(f"live version is still {live_after}: the bad build never stayed live.")


if __name__ == "__main__":
    main()
