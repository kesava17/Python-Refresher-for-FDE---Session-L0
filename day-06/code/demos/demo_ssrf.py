"""Server-Side Request Forgery (security): validate where a URL points before fetching.

The concept, in plain words:
    Some features fetch a URL the user gave you: an avatar, a webhook, a "preview this
    link" box. The danger is that your server, unlike the user's browser, sits inside
    your private network and often next to a cloud metadata service at 169.254.169.254
    that hands out credentials. If you fetch whatever URL arrives, an attacker points it
    at that metadata address, or at localhost, or at an internal admin page, and your
    server fetches it for them. The fix is to resolve the host, check the resolved
    address, and reject loopback, private, and link-local ranges before making any
    request. An allowlist of hosts you actually intend to call is stronger still.

Why a fresher should care:
    "Fetch the URL the user typed" feels innocent and is one of the most common ways
    cloud credentials get stolen. The check is not the HTTP call; it is what you do
    before it: resolve, inspect the address, and refuse anything internal.

What this demo shows:
    A fetch function that resolves the host, blocks loopback and private and link-local
    addresses, and also enforces an allowlist. The metadata address and localhost are
    rejected; an allowed public host passes. No real network call is made: the fetch is
    simulated after the check passes, so the demo is offline and deterministic.

Run:  poetry run python demo_ssrf.py
"""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

# Hosts we actually intend to call. Anything else is refused even if it is public.
# The last one is allowlisted but (see FAKE_DNS) resolves to loopback, to show the
# address check catching what the allowlist alone would let through.
ALLOWED_HOSTS = {"images.example.com", "cdn.example.com", "cdn.example.com.attacker"}

# A tiny fixed name-to-address map so the demo resolves hosts without real DNS.
FAKE_DNS: dict[str, str] = {
    "images.example.com": "93.184.216.34",  # a normal public address
    "cdn.example.com": "93.184.216.35",
    "localhost": "127.0.0.1",
    "metadata.internal": "169.254.169.254",  # cloud metadata, link-local
    "db.internal": "10.0.0.5",  # private range
    # An allowlisted name that resolves to loopback. This models DNS rebinding:
    # the attacker controls (or has poisoned) a name you trust and points it inward.
    "cdn.example.com.attacker": "127.0.0.1",
}


class BlockedRequest(Exception):
    """Raised when a URL fails validation, before any request is attempted."""


def resolve_host(host: str) -> str:
    """Stand-in for DNS resolution. A real server would call the resolver here."""
    if host not in FAKE_DNS:
        raise BlockedRequest(f"host does not resolve: {host}")
    return FAKE_DNS[host]


def check_url_is_safe(url: str) -> str:
    """Validate the URL and return its resolved address, or raise BlockedRequest."""
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise BlockedRequest(f"scheme not allowed: {parts.scheme!r}")

    host = parts.hostname or ""
    if host not in ALLOWED_HOSTS:
        raise BlockedRequest(f"host not on allowlist: {host!r}")

    # Resolve, then judge the actual address. This is what stops a host that
    # resolves to an internal address from sneaking through.
    address = ipaddress.ip_address(resolve_host(host))
    if address.is_loopback or address.is_private or address.is_link_local:
        raise BlockedRequest(f"resolved to an internal address: {address}")
    return str(address)


def fetch_url(url: str) -> str:
    """Check first, then 'fetch'. The fetch is simulated to keep the demo offline."""
    address = check_url_is_safe(url)
    # A real implementation would call httpx.get(url) here, pinned to `address`.
    return f"(simulated 200 OK from {address})"


def main() -> None:
    candidates = [
        "http://metadata.internal/latest/meta-data/",  # blocked: not on allowlist
        "http://localhost/admin",  # blocked: not on allowlist
        "http://db.internal:5432/",  # blocked: not on allowlist
        # Blocked by the address check, not the allowlist: it is allowlisted but
        # resolves to loopback (DNS rebinding). This is why we check the address too.
        "https://cdn.example.com.attacker/latest/meta-data/",
        "https://images.example.com/avatar/P-77.png",  # legitimate, allowed
    ]
    for url in candidates:
        try:
            result = fetch_url(url)
            print(f"ALLOWED  {url}\n         {result}")
        except BlockedRequest as exc:
            print(f"BLOCKED  {url}\n         {exc}")


if __name__ == "__main__":
    main()
