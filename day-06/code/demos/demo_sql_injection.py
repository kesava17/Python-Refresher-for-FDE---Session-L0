"""SQL injection (security): build queries with parameters, never with string glue.

The concept, in plain words:
    When you paste user input straight into a SQL string, the input can stop being data
    and start being code. A product_id of "x' OR '1'='1" turns a "find one product"
    query into "find every row", because the quote closes the string and the OR makes
    the condition always true. The fix is a parameterized query: you leave a placeholder
    (?) in the SQL and hand the value separately, so the database always treats it as
    one value, never as query syntax.

Why a fresher should care:
    String-built SQL is the classic way data leaks and gets destroyed. The fix costs
    nothing: use placeholders. Every database library supports them, and they also make
    the code cleaner. There is no good reason to concatenate user input into SQL.

What this demo shows:
    A real in-memory SQLite table of reviews. The unsafe query concatenates the input,
    so the payload "x' OR '1'='1" returns every row. The safe query uses a ?
    placeholder, so the same payload matches no product and returns nothing.

Run:  poetry run python demo_sql_injection.py
"""

from __future__ import annotations

import sqlite3


def build_reviews_table() -> sqlite3.Connection:
    """Create an in-memory table with a few reviews under two product ids."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE reviews (id TEXT, product_id TEXT, text TEXT)")
    conn.executemany(
        "INSERT INTO reviews VALUES (?, ?, ?)",
        [
            ("R-1", "P-77", "Great mixer, quiet motor."),
            ("R-2", "P-77", "Solid build, five stars."),
            ("R-3", "P-88", "Battery drains fast."),
        ],
    )
    conn.commit()
    return conn


def find_reviews_unsafe(conn: sqlite3.Connection, product_id: str) -> list[str]:
    """UNSAFE: glue the input into the SQL text, so input can become query code."""
    # Never do this. The input is pasted straight into the query string.
    query = f"SELECT id FROM reviews WHERE product_id = '{product_id}'"
    return [row[0] for row in conn.execute(query).fetchall()]


def find_reviews_safe(conn: sqlite3.Connection, product_id: str) -> list[str]:
    """SAFE: a ? placeholder keeps the input as one value, never as query syntax."""
    query = "SELECT id FROM reviews WHERE product_id = ?"
    return [row[0] for row in conn.execute(query, (product_id,)).fetchall()]


def main() -> None:
    conn = build_reviews_table()

    # The attack payload closes the quote and adds an always-true OR.
    payload = "x' OR '1'='1"

    leaked = find_reviews_unsafe(conn, payload)
    print(f"unsafe query with payload -> returned {len(leaked)} rows: {leaked}")
    print("  the whole table leaked, because the input became SQL code")

    blocked = find_reviews_safe(conn, payload)
    print(f"safe query with payload   -> returned {len(blocked)} rows: {blocked}")
    print("  no product literally has that id, so the parameterized query matches none")

    # Proof the safe query still works for a real id.
    real = find_reviews_safe(conn, "P-77")
    print(f"safe query with real id   -> returned {len(real)} rows: {real}")

    conn.close()


if __name__ == "__main__":
    main()
