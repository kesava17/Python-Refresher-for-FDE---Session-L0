"""Secret scanning (security): catch hard-coded credentials before they are committed.

The concept, in plain words:
    Secrets belong in a vault or an environment variable, never typed into source code.
    But they get pasted in "just to test", and then committed, and then they live in git
    history forever. A secret scanner is a small tool, usually a pre-commit hook, that
    reads the diff and looks for the tell-tale shapes of secrets: a "sk_live_" API key,
    a password assigned to a variable, a long token. If it finds one, it stops the
    commit and points at the line, so the secret never reaches the repository.

Why a fresher should care:
    A leaked key in a public repo is found by bots within minutes and used to run up
    bills or steal data. You will paste a secret to test something one day; a scanner is
    the net that catches it. Understanding the patterns also tells you what NOT to write
    in code.

What this demo shows:
    A code sample with a couple of planted secrets. A handful of regexes scan it line by
    line and report each hit with its line number and a redacted preview, the way a real
    pre-commit scanner reports findings.

Run:  poetry run python demo_secret_scan.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A code sample to scan. In real life this would be the staged diff.
CODE_SAMPLE = '''\
import os

# Fine: read the secret from the environment at runtime.
DB_URL = os.environ["DB_URL"]

# Planted problems the scanner should catch:
STRIPE_KEY = ""
def connect():
    password = "hunter2-not-a-real-password"
    return password

# A generic long token pasted into a header.
AUTH_HEADER = "Bearer "
'''


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]


# Each rule names what it finds and the shape it looks for.
RULES: list[Rule] = [
    Rule("stripe_live_key", re.compile(r"sk_live_[A-Za-z0-9]{16,}")),
    Rule("password_assignment", re.compile(r"(?i)password\s*=\s*['\"][^'\"]{6,}['\"]")),
    Rule("bearer_token", re.compile(r"Bearer\s+[A-Za-z0-9]{24,}")),
]


def redact(text: str) -> str:
    """Show enough of a hit to recognize it, but never print the whole secret."""
    text = text.strip()
    if len(text) <= 8:
        return "*" * len(text)
    return f"{text[:6]}...{text[-2:]}"


def scan(code: str) -> list[tuple[int, str, str]]:
    """Return (line number, rule name, redacted match) for every secret found."""
    findings: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(code.splitlines(), start=1):
        for rule in RULES:
            match = rule.pattern.search(line)
            if match:
                findings.append((line_number, rule.name, redact(match.group(0))))
    return findings


def main() -> None:
    findings = scan(CODE_SAMPLE)
    if not findings:
        print("no secrets found")
        return
    print(f"found {len(findings)} likely secret(s):")
    for line_number, rule_name, preview in findings:
        print(f"  line {line_number:>2}: {rule_name:<20} {preview}")
    print("\na pre-commit hook would stop the commit until these are removed")


if __name__ == "__main__":
    main()
