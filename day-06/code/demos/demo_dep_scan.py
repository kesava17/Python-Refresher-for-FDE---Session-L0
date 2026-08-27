"""Dependency scanning (security): your code is only as safe as the libraries you pin.

The concept, in plain words:
    Most of the code that ships is code you did not write: your dependencies, and their
    dependencies. When a vulnerability is found in one of them, a fix is released in a
    new version, and everyone still on the old version is exposed. A dependency scanner
    compares your pinned versions against a database of known advisories and reports any
    match: which package, which version, and which advisory. In CI it fails the build so
    a known-vulnerable version cannot ship.

Why a fresher should care:
    You will spend more time picking and updating dependencies than you expect, and "we
    never upgraded that library" is a very common root cause of breaches. The scanner is
    what turns a public advisory into a build failure you cannot ignore.

What this demo shows:
    A small hard-coded advisory database and a pinned requirements list with one library
    on a known-bad version. The scan matches the pin against the advisories and prints
    the finding, the way a CI step would. Everything is local; there is no network call.

Run:  poetry run python demo_dep_scan.py
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Advisory:
    package: str
    affected_versions: frozenset[str]  # kept simple: exact versions, no range parsing
    advisory_id: str
    summary: str
    fixed_in: str


# A tiny stand-in for a real advisory feed (like the Python Packaging Advisory DB).
ADVISORY_DB: list[Advisory] = [
    Advisory(
        package="requests",
        affected_versions=frozenset({"2.19.0", "2.19.1"}),
        advisory_id="ADV-2018-0001",
        summary="Credentials leaked to the destination on cross-host redirect.",
        fixed_in="2.20.0",
    ),
    Advisory(
        package="pyyaml",
        affected_versions=frozenset({"5.1", "5.2", "5.3"}),
        advisory_id="ADV-2020-0002",
        summary="Arbitrary code execution via full_load on untrusted input.",
        fixed_in="5.4",
    ),
]


# Our pinned dependencies (package, version). One of them is on a known-bad version.
PINNED: list[tuple[str, str]] = [
    ("requests", "2.19.1"),  # known-vulnerable
    ("pyyaml", "6.0"),  # safe: past the affected range
    ("httpx", "0.28.1"),  # not in the advisory db at all
]


@dataclass(frozen=True)
class Finding:
    package: str
    version: str
    advisory_id: str
    summary: str
    fixed_in: str


def scan(pinned: list[tuple[str, str]]) -> list[Finding]:
    """Match each pinned package/version against the advisory database."""
    findings: list[Finding] = []
    for package, version in pinned:
        for advisory in ADVISORY_DB:
            if advisory.package == package and version in advisory.affected_versions:
                findings.append(
                    Finding(
                        package=package,
                        version=version,
                        advisory_id=advisory.advisory_id,
                        summary=advisory.summary,
                        fixed_in=advisory.fixed_in,
                    )
                )
    return findings


def main() -> None:
    findings = scan(PINNED)
    if not findings:
        print("no known-vulnerable dependencies found")
        return
    print(f"found {len(findings)} vulnerable dependency(ies):")
    for f in findings:
        print(f"  {f.package} {f.version}  [{f.advisory_id}]")
        print(f"    {f.summary}")
        print(f"    fix: upgrade to {f.fixed_in} or later")
    print("\na CI dependency scan would fail the build on this finding")


if __name__ == "__main__":
    main()
