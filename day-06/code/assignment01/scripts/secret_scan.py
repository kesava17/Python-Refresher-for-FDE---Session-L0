"""A tiny hard-coded-secret scanner for the source tree.

Secrets belong in the environment, never in the source, where they would be committed to
history and shared with everyone who can read the repository. This script scans the Python
files under `src/` for the common shapes of a hard-coded secret and exits non-zero if it finds
one, so it can run in a pre-commit hook or a CI gate and fail the build before a secret lands.

It is deliberately dependency-light (standard library `re` only) and deliberately narrow: it
flags a secret-like name assigned directly to a string literal, plus a couple of well-known
credential markers. Lines that read from the environment are exempt, because reading from the
environment is exactly the pattern we want. Run it directly:

    python scripts/secret_scan.py
"""

from __future__ import annotations

import re
from pathlib import Path

# The project root is the parent of this scripts/ directory, so the scan target is resolved the
# same way no matter which directory the script is run from.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_TARGET = _PROJECT_ROOT / "src"

# A secret-like variable name assigned directly to a string literal, for example
# `password = "hunter2"` or `API_KEY = 's3cr3t'`. We do not include a bare "key", which is too
# common a variable name to be useful, only the specific credential names.
_ASSIGNED_SECRET = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|apikey|access[_-]?key"
    r"|auth[_-]?token|private[_-]?key)\b\s*[:=]\s*['\"][^'\"]{3,}['\"]"
)

# An AWS access key id has a fixed, recognizable shape.
_AWS_ACCESS_KEY = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# The header line of a PEM-encoded private key.
_PRIVATE_KEY_HEADER = re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")

_PATTERNS = (_ASSIGNED_SECRET, _AWS_ACCESS_KEY, _PRIVATE_KEY_HEADER)


def _is_exempt(line: str) -> bool:
    # A comment is documentation, not a live secret, so skip it. A line that reads from the
    # environment is the pattern we want, so skip it too even if it names a secret.
    stripped = line.strip()
    if stripped.startswith("#"):
        return True
    return "os.environ" in line or "getenv" in line


def find_secrets(root: Path) -> list[str]:
    """Return one human-readable finding per suspected hard-coded secret under `root`."""
    findings: list[str] = []
    for path in sorted(root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if _is_exempt(line):
                continue
            if any(pattern.search(line) for pattern in _PATTERNS):
                findings.append(f"{path}:{line_no}: possible hard-coded secret")
    return findings


def main() -> int:
    findings = find_secrets(_DEFAULT_TARGET)
    if findings:
        # Print every finding, then fail so a gate can stop the build.
        for finding in findings:
            print(finding)
        print(f"secret scan: {len(findings)} finding(s)")
        return 1
    print("secret scan: no hard-coded secrets found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
