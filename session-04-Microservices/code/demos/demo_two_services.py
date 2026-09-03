"""Two services talking over HTTP: an orders service calls an inventory service.

One idea, isolated: in a microservice system a call between services crosses the network, so
it is an HTTP request, not a function call. That boundary is what makes each service
independently deployable, and it is also what can be slow or fail. Standard library only.

Run:  poetry run python demo_two_services.py
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.request import urlopen


def _make_handler(payload: dict[str, Any]) -> type[BaseHTTPRequestHandler]:
    """Build a handler class that answers any GET with the given JSON payload."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (name fixed by http.server)
            """Return the payload as JSON."""
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            """Silence the default request logging."""

    return Handler


def serve(payload: dict[str, Any]) -> HTTPServer:
    """Start a background HTTP service on an ephemeral port and return the server."""
    server = HTTPServer(("127.0.0.1", 0), _make_handler(payload))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> None:
    """Start an inventory service and have an orders service call it over HTTP."""
    inventory = serve({"sku": "A-100", "in_stock": 7})
    port = inventory.server_address[1]
    print(f"inventory service listening on 127.0.0.1:{port}")

    with urlopen(f"http://127.0.0.1:{port}/stock", timeout=2.0) as response:
        data = json.loads(response.read())
    print(f"orders service called inventory over HTTP -> {data}")

    print("\nThe call crossed a real HTTP boundary, not a function call. That boundary is")
    print("what lets the two services deploy on their own, and what a timeout has to guard.")
    inventory.shutdown()


if __name__ == "__main__":
    main()
