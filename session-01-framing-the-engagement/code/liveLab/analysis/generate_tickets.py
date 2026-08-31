"""Generate a realistic one-week sample of Sunrise Electronics support tickets.

Seeded for reproducibility. The distribution is deliberately Pareto-shaped: three
question types (order_status, return, warranty_simple) make up about 60 percent of
all tickets, and a long tail of many rarer types makes up the rest. Trainees run a
Pareto analysis on the output and should rediscover that vital few.

Run:  python generate_tickets.py
Out:  ../data/support_tickets.csv
"""

from __future__ import annotations

import csv
import os
import random
from datetime import datetime, timedelta

SEED = 42
N_TICKETS = 4000
WEEK_START = datetime(2026, 8, 3, 0, 0, 0)  # a Monday

# question_type -> (weight, handle_time_range_min, escalation_prob, csat_bias)
# The first three are the vital few (~60%). The rest are the long tail (~40%).
TYPES: dict[str, tuple[float, tuple[int, int], float, float]] = {
    "order_status":       (0.30, (3, 9),   0.04, 0.1),
    "return":             (0.18, (5, 14),  0.08, 0.0),
    "warranty_simple":    (0.12, (6, 16),  0.10, -0.1),
    # long tail
    "delivery_delay":     (0.06, (6, 18),  0.15, -0.3),
    "product_info":       (0.05, (4, 12),  0.05, 0.2),
    "payment_issue":      (0.04, (8, 22),  0.20, -0.4),
    "account_login":      (0.035, (5, 15), 0.12, -0.1),
    "warranty_dispute":   (0.03, (20, 45), 0.55, -0.8),
    "exchange":           (0.03, (7, 18),  0.10, 0.0),
    "cancellation":       (0.025, (5, 14), 0.10, -0.1),
    "refund_status":      (0.025, (5, 13), 0.12, -0.3),
    "technical_setup":    (0.02, (18, 40), 0.35, -0.2),
    "price_match":        (0.015, (8, 20), 0.18, -0.2),
    "damaged_item":       (0.015, (10, 25),0.30, -0.5),
    "store_hours":        (0.01, (2, 5),   0.01, 0.4),
    "feedback_complaint": (0.01, (10, 30), 0.25, -0.6),
    "gift_card":          (0.008, (6, 16), 0.15, -0.1),
    "bulk_order":         (0.007, (15, 35),0.30, 0.0),
    "other":              (0.02, (6, 20),  0.20, -0.2),
}

SUBJECTS: dict[str, list[str]] = {
    "order_status": [
        "Where is my order {oid}?",
        "Order {oid} not delivered yet",
        "Tracking for {oid} not updating",
        "When will {oid} arrive?",
        "Status of my phone order {oid}",
    ],
    "return": [
        "How do I return {oid}?",
        "Return process for a headset",
        "Want to return the mixer, order {oid}",
        "Return label not received",
        "Can I return an opened item?",
    ],
    "warranty_simple": [
        "Is my {item} under warranty?",
        "Warranty period for order {oid}",
        "How to claim warranty on {item}",
        "Warranty registration for {item}",
        "Does the {item} have warranty?",
    ],
    "delivery_delay": ["Delivery is late for {oid}", "Courier missed delivery {oid}"],
    "product_info": ["Does the {item} support fast charging?", "Specs for the {item}"],
    "payment_issue": ["Payment failed for {oid}", "Charged twice for {oid}"],
    "account_login": ["Cannot log in to my account", "Reset my password"],
    "warranty_dispute": [
        "Warranty claim rejected for {item}",
        "Disagree with warranty decision on {oid}",
    ],
    "exchange": ["Exchange {item} for a different size", "Wrong color delivered {oid}"],
    "cancellation": ["Cancel order {oid}", "Please cancel {oid} before dispatch"],
    "refund_status": ["Refund not received for {oid}", "When will my refund come?"],
    "technical_setup": ["{item} will not turn on", "Help setting up the {item}"],
    "price_match": ["Price dropped after I bought {oid}", "Price match request"],
    "damaged_item": ["Received a damaged {item}", "{item} arrived broken, order {oid}"],
    "store_hours": ["What time does the Pune store open?", "Store hours on Sunday"],
    "feedback_complaint": ["Very poor service", "Complaint about support"],
    "gift_card": ["Gift card balance check", "Gift card not working"],
    "bulk_order": ["Bulk order for office", "Corporate purchase enquiry"],
    "other": ["General question", "Not sure who to ask"],
}

ITEMS = ["phone", "mixer grinder", "headset", "smart TV", "laptop", "power bank",
         "air fryer", "washing machine", "router", "earbuds"]
CHANNELS = [("email", 0.45), ("chat", 0.40), ("phone", 0.15)]


def weighted_choice(rng: random.Random, pairs: list[tuple[str, float]]) -> str:
    r = rng.random() * sum(w for _, w in pairs)
    upto = 0.0
    for name, w in pairs:
        upto += w
        if r <= upto:
            return name
    return pairs[-1][0]


def main() -> None:
    rng = random.Random(SEED)
    type_pairs = [(t, cfg[0]) for t, cfg in TYPES.items()]

    rows = []
    for i in range(1, N_TICKETS + 1):
        qtype = weighted_choice(rng, type_pairs)
        _, (lo, hi), esc_p, csat_bias = TYPES[qtype]

        # timestamp: spread across a 7-day week, weighted to business hours
        day = rng.randint(0, 6)
        hour = int(min(23, max(0, rng.gauss(13, 3.2))))
        minute = rng.randint(0, 59)
        created = WEEK_START + timedelta(days=day, hours=hour, minutes=minute)

        item = rng.choice(ITEMS)
        oid = f"SE-{rng.randint(100000, 999999)}"
        subject = rng.choice(SUBJECTS[qtype]).format(oid=oid, item=item)

        handle_time = rng.randint(lo, hi)
        escalated = rng.random() < esc_p
        # csat 1..5, biased by type; blank ~20% of the time (not every ticket rated)
        if rng.random() < 0.20:
            csat = ""
        else:
            base = rng.gauss(4.0 + csat_bias, 0.8)
            csat = str(max(1, min(5, round(base))))

        channel = weighted_choice(rng, CHANNELS)
        rows.append([
            f"T{i:05d}", created.strftime("%Y-%m-%d %H:%M"), channel, qtype,
            subject, handle_time, "yes" if escalated else "no", csat,
        ])

    rows.sort(key=lambda r: r[1])  # by created_at

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "support_tickets.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ticket_id", "created_at", "channel", "question_type",
                    "subject", "handle_time_min", "escalated", "csat"])
        w.writerows(rows)

    print(f"wrote {len(rows)} tickets to {os.path.normpath(out_path)}")


if __name__ == "__main__":
    main()
