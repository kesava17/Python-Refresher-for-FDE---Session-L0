"""Shed load past a concurrency limit (reliability): a fast no beats a slow collapse.

The concept, in plain words:
    Every service has a limit to how much work it can run at once and still stay fast.
    When more work arrives than that limit, you have a choice. You can accept all of it
    and let everything slow to a crawl, or you can accept up to the limit and reject the
    rest immediately with a "try again later" (an HTTP 429). Rejecting fast keeps the
    accepted work inside its latency target instead of dragging everyone down together.

Why a fresher should care:
    A queue that grows without bound turns one spike into a full outage: every request
    gets slow, then times out. A concurrency cap with fast rejection protects the
    requests you did accept.

What this demo shows:
    A cap of 4 in-flight requests. Ten requests arrive at once. The first 4 are accepted
    and complete within the 50 ms target; the remaining 6 are shed instantly with a 429
    marker. We print the split and confirm the accepted work kept its target.

Run:  poetry run python demo_load_shedding.py
"""

from __future__ import annotations

CONCURRENCY_LIMIT = 4  # how many requests we can run at once and still hit the target
LATENCY_TARGET_MS = 50  # accepted work must finish within this
WORK_LATENCY_MS = 40  # how long one accepted unit of work takes (within target)
OFFERED = 10  # how many requests arrive in the burst


def main() -> None:
    accepted: list[dict[str, int | str]] = []
    shed: list[dict[str, str]] = []

    for request_id in range(1, OFFERED + 1):
        if len(accepted) < CONCURRENCY_LIMIT:
            # Under the cap: admit the request. It runs within the latency target.
            accepted.append(
                {"id": request_id, "status": "ok", "latency_ms": WORK_LATENCY_MS}
            )
        else:
            # Over the cap: reject at once with a 429, so we never build an
            # unbounded queue.
            shed.append({"id": str(request_id), "status": "429 shed"})

    print(f"offered  : {OFFERED} requests, concurrency limit {CONCURRENCY_LIMIT}")
    print(f"accepted : {len(accepted)}  -> {[r['id'] for r in accepted]}")
    print(f"shed     : {len(shed)}  -> {[r['id'] for r in shed]} (429, shed)")

    worst = max(int(r["latency_ms"]) for r in accepted)
    within = worst <= LATENCY_TARGET_MS
    print(
        f"accepted work worst latency {worst} ms vs {LATENCY_TARGET_MS} ms target: "
        f"{'within target' if within else 'MISSED target'}"
    )


if __name__ == "__main__":
    main()
