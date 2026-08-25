"""Track an error budget and alert on fast burn (reliability): a measurable promise.

The concept, in plain words:
    A service level objective (SLO) is a target like "99 percent of requests succeed
    this month". The 1 percent you are allowed to fail is your error budget. If you
    spend that budget too fast early in the window, you will run out before the month
    ends and miss the objective. A burn check watches the spend rate and warns while
    there is still time to react.

Why a fresher should care:
    "Is it up?" is a yes or no with no room to plan. An error budget turns reliability
    into a number you can watch draining, so an alert fires before customers feel a full
    outage.

What this demo shows:
    A fixed stream of 1000 requests with 40 failures at known positions, against a 99
    percent objective (budget = 10 failures). We report the running failure count at
    intervals and, because 40 failures is far past the 10 we were allowed, end with a
    clear ALERT line.

Run:  poetry run python demo_slo_burn.py
"""

from __future__ import annotations

TOTAL_REQUESTS = 1000
OBJECTIVE = 0.99  # 99 percent of requests should succeed over the window
ERROR_BUDGET = round(TOTAL_REQUESTS * (1 - OBJECTIVE))  # failures allowed all month


def build_stream() -> list[bool]:
    """Return a fixed outcome per slot: True means success, False means failure.

    Failures sit at fixed positions (every 25th request), so the run is fully
    deterministic: 40 failures across 1000 requests, four times the budget of 10.
    """
    return [(i % 25) != 0 for i in range(TOTAL_REQUESTS)]


def main() -> None:
    stream = build_stream()
    print(f"objective={OBJECTIVE:.0%}  total={TOTAL_REQUESTS}  budget={ERROR_BUDGET}")

    failures = 0
    for index, ok in enumerate(stream, start=1):
        if not ok:
            failures += 1
        # Report at each quarter of the stream so we can watch the budget drain.
        if index % 250 == 0:
            spent = failures / ERROR_BUDGET  # fraction of month budget used so far
            elapsed = index / TOTAL_REQUESTS  # fraction of the window elapsed so far
            pace = "too fast" if spent > elapsed else "on pace"
            print(
                f"  at {index:>4} requests: {failures:>2} failures, "
                f"budget spent {spent:>5.0%}, window elapsed {elapsed:>4.0%} ({pace})"
            )

    print(f"final: {failures} failures against a budget of {ERROR_BUDGET}")
    if failures > ERROR_BUDGET:
        print("budget burned too fast: ALERT")
    else:
        print("within budget")


if __name__ == "__main__":
    main()
