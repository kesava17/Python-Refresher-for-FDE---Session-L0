"""Correlate logs with a trace id (Level 1.8): one id ties one request's logs across services.

The concept, in plain words:
    A single request often touches several services on its way through. When something goes wrong,
    you need to line up the log lines that belong to that one request, out of thousands from every
    other request happening at the same time. The trick is to mint one id at the edge and pass it
    down through every call. Every log line carries that id, so you can filter by it and read the
    whole story.

Why a fresher should care:
    Without a shared id, cross-service debugging is guesswork over timestamps. With one, you search
    for the id and every hop lines up. This is the backbone of distributed tracing, and the idea is
    as simple as passing one extra argument.

What this demo shows:
    The edge creates a uuid trace_id and passes it into two fake service calls. Each service prints
    a log line that includes the id, so all the lines for this one request share the same id, while
    a second request gets its own.

Run:  poetry run python demo_trace_id.py
"""

from __future__ import annotations

import uuid


def log(trace_id: str, service: str, message: str) -> None:
    """Print one structured-ish log line. The trace id leads, so lines are easy to group."""
    print(f"trace={trace_id} service={service:<13} {message}")


def rating_service(trace_id: str, product_id: str) -> float:
    # A downstream service. It does its work and logs under the same id it was handed.
    log(trace_id, "rating", f"averaging ratings for {product_id}")
    return 4.2


def summary_service(trace_id: str, product_id: str, average: float) -> str:
    # Another downstream service. Same id again, so its line sits with the others.
    log(trace_id, "summary", f"building summary for {product_id} (avg {average})")
    return f"{product_id}: {average} stars"


def handle_request(product_id: str) -> str:
    """The edge: mint one trace id for this request and thread it through every call."""
    trace_id = str(uuid.uuid4())
    log(trace_id, "edge", f"received request for {product_id}")
    average = rating_service(trace_id, product_id)
    return summary_service(trace_id, product_id, average)


def main() -> None:
    # Two independent requests. Within each, every line shares one id; across them, the ids differ.
    print("--- request one ---")
    print("result:", handle_request("P1"))
    print("--- request two ---")
    print("result:", handle_request("P2"))
    print("\nFilter the output by one trace id and you see just that request's path.")


if __name__ == "__main__":
    main()
