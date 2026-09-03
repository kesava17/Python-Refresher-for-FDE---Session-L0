"""A circuit breaker: stop calling a failing dependency, then let it recover.

After a run of failures the breaker opens, so the caller fails fast instead of throwing every
request into a dead service. After a cooldown it half-opens to try again. An injectable clock
keeps this deterministic. Standard library only.

Run:  poetry run python demo_circuit_breaker.py
"""

from __future__ import annotations

from collections.abc import Callable


class CircuitBreaker:
    """Track failures to a dependency; open at a threshold, recover after a cooldown."""

    def __init__(
        self, threshold: int = 3, cooldown: float = 5.0, now: Callable[[], float] | None = None
    ) -> None:
        """Configure the breaker; `now` is injectable so the demo needs no real clock."""
        self.threshold = threshold
        self.cooldown = cooldown
        self._now = now or (lambda: 0.0)
        self._failures = 0
        self._opened_at: float | None = None

    def is_open(self) -> bool:
        """Return True while open; after the cooldown, half-open for a trial."""
        if self._opened_at is None:
            return False
        if self._now() - self._opened_at >= self.cooldown:
            self._opened_at = None
            self._failures = 0
            return False
        return True

    def record_failure(self) -> None:
        """Count a failure and open the breaker once the threshold is reached."""
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = self._now()


def main() -> None:
    """Open the breaker with three failures, then recover after the cooldown."""
    clock = [0.0]
    breaker = CircuitBreaker(threshold=3, cooldown=5.0, now=lambda: clock[0])

    print("three failures in a row open the circuit:")
    for i in range(1, 4):
        breaker.record_failure()
        print(f"  failure {i}: open={breaker.is_open()}")
    print("  the caller now fails fast, without even trying the dead dependency\n")

    print("after the cooldown, the circuit half-opens for a trial:")
    clock[0] = 6.0
    print(f"  open={breaker.is_open()} (a trial call is allowed again)")


if __name__ == "__main__":
    main()
