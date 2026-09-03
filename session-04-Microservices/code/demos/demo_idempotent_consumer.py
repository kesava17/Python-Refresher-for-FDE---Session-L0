"""At-least-once delivery means duplicates. An idempotent consumer handles them safely.

A message stream redelivers one event; the consumer keys on the event id and skips the
duplicate, so the running total stays correct. This is the property that makes asynchronous
messaging safe. Standard library only.

Run:  poetry run python demo_idempotent_consumer.py
"""

from __future__ import annotations


def main() -> None:
    """Consume a stream that redelivers one event, without double-counting it."""
    events = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 5},
        {"id": 1, "value": 10},  # a redelivery of event 1
        {"id": 3, "value": 7},
    ]

    seen: set[int] = set()
    total = 0
    count = 0
    print("consuming a stream that redelivers event 1:")
    for event in events:
        event_id = int(event["id"])
        if event_id in seen:
            print(f"  event {event_id}: duplicate, skipped")
            continue
        seen.add(event_id)
        total += int(event["value"])
        count += 1
        print(f"  event {event_id}: applied (count={count}, total={total})")

    print(f"\nfinal: {count} events applied, total {total}. The duplicate did not double-count,")
    print("because the consumer is idempotent on the event id.")


if __name__ == "__main__":
    main()
