"""A small secret scanner for CI (the secure topic): fail the build on a hard-coded secret.

Secrets belong in the environment (or a secret manager), never committed to source. This script
walks the source tree and looks for the shapes secrets usually take: cloud access keys, private
key blocks, and a secret-looking value assigned straight to a secret-named variable. If it finds
one it prints where (never the value itself) and exits non-zero, so a CI step can block the merge.

Run it directly for the CI proof:

    poetry run python scripts/secret_scan.py

It scans src/ by default and exits 0 when the source is clean. The tests import scan_source and
assert the real source has zero findings.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Each pattern targets a real secret shape, not an English word. The assignment pattern requires
# a secret-named variable set directly to a quoted literal of some length, which is the classic
# "hard-coded credential" mistake. It does not fire on a value read through os.environ.get(...),
# because there the quote does not sit right after the "=".
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "private_key_block",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "hardcoded_secret_assignment",
        re.compile(
            r"(?i)(password|passwd|secret|api[_-]?key|access[_-]?key|token)"
            r"""\s*[:=]\s*["'][^"']{12,}["']"""
        ),
    ),
]

# src/reviews_insight/config.py has parents: [reviews_insight, src, project_root]. This file is at
# scripts/secret_scan.py, so its parent's parent is the project root, and src is beside scripts.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_SRC = _PROJECT_ROOT / "src"


@dataclass(frozen=True)
class Finding:
    """One suspected secret: where it is and which pattern matched. The value is never kept."""

    path: Path
    line: int
    pattern: str


def scan_text(text: str) -> list[str]:
    """Return the names of the patterns that match anywhere in a block of text."""
    return [name for name, pattern in _PATTERNS if pattern.search(text)]


def scan_source(root: Path = _DEFAULT_SRC) -> list[Finding]:
    """Scan every Python file under root and return one Finding per matching line."""
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for name in scan_text(line):
                findings.append(Finding(path=path, line=number, pattern=name))
    return findings


def main() -> int:
    """Scan src/ and exit non-zero if anything looks like a hard-coded secret."""
    findings = scan_source()
    if not findings:
        print(f"secret scan: no findings under {_DEFAULT_SRC}")
        return 0
    for finding in findings:
        # Report the location and the rule, never the matched text, so the report itself is safe.
        relative = finding.path.relative_to(_PROJECT_ROOT)
        print(f"secret scan: {relative}:{finding.line} matched {finding.pattern}")
    print(f"secret scan: {len(findings)} finding(s); failing the build")
    return 1


if __name__ == "__main__":
    sys.exit(main())
