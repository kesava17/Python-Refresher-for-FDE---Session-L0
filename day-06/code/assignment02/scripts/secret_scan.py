"""A small secret scanner (Secure topic): fail the build when a secret is hard-coded in src.

Secrets belong in the environment or a secret store, never in source and never in a container
image. This script scans the src/ tree for the shapes a leaked secret usually takes: a private
key block, a cloud access key, a known token prefix, or a secret-named variable bound directly to
a string literal. It prints each finding and exits non-zero when it finds one, so it can gate a
commit or a pipeline. Run it with: poetry run python scripts/secret_scan.py

It uses only the standard library (re, pathlib, sys), so it runs anywhere Python does, with no
install step.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Each pattern names one shape a hard-coded secret takes. The names make a finding readable, so a
# developer can see at a glance what tripped the scan.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # A PEM private key block: the single strongest signal that a real key leaked into source.
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    # An AWS access key id has a fixed prefix and length.
    ("aws access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    # Common token prefixes from well known providers (GitHub, Slack).
    ("provider token", re.compile(r"(?:ghp_[0-9A-Za-z]{20,}|xox[baprs]-[0-9A-Za-z-]{10,})")),
    # A secret-named variable bound directly to a string literal. This is the everyday mistake the
    # scan is really about: writing the secret into the code instead of reading it from the
    # environment. A value sourced from os.environ or os.getenv starts with a name, not a quote, so
    # it does not match here, which is exactly the safe pattern we want to allow.
    (
        "secret bound to a literal",
        re.compile(
            r"(?i)(?:password|passwd|secret|token|api[_-]?key|access[_-]?key)"
            r"\s*[:=]\s*['\"][^'\"]{6,}['\"]"
        ),
    ),
]


@dataclass(frozen=True)
class Finding:
    """One place where the scan matched, with enough context to fix it."""

    path: Path
    line_number: int
    rule: str
    text: str


def scan_text(text: str, path: Path) -> list[Finding]:
    """Return every finding in one file's text, one per matching line and rule."""
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for rule, pattern in _PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path, number, rule, line.strip()))
    return findings


def scan_directory(root: Path) -> list[Finding]:
    """Scan every Python file under root and return all findings."""
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.py")):
        # Read as text and ignore undecodable bytes, so a stray binary file never crashes the scan.
        findings.extend(scan_text(path.read_text(encoding="utf-8", errors="ignore"), path))
    return findings


def main() -> int:
    """Scan the project's src/ tree and return a process exit code: 0 clean, 1 on any finding."""
    # The script lives in scripts/, so src/ is its sibling. Resolving from __file__ keeps the scan
    # working no matter which directory it is launched from.
    src_root = Path(__file__).resolve().parent.parent / "src"
    findings = scan_directory(src_root)
    if not findings:
        print(f"secret scan: 0 findings across {src_root}")
        return 0
    for finding in findings:
        print(f"{finding.path}:{finding.line_number}: [{finding.rule}] {finding.text}")
    print(f"secret scan: {len(findings)} finding(s); failing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
