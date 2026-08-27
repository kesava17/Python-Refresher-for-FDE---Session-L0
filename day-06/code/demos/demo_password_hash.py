"""Password storage (security): salt and slow-hash; never store or fast-hash passwords.

The concept, in plain words:
    You must never store a password itself. You store a hash, a one-way fingerprint, so
    a stolen database does not hand over the passwords. Two rules make that safe. First,
    a per-password random salt: without it, identical passwords hash to identical values
    and attackers precompute huge lookup tables. With a salt, every stored hash is
    unique even for the same password. Second, a slow, memory-hard function like scrypt:
    a deliberately expensive hash means an attacker can only try a few guesses per
    second, not billions. A fast hash like a bare SHA-256 is the opposite of what you
    want here.

    This demo uses hashlib.scrypt because it is in the standard library. In production
    the common choices are bcrypt or argon2 (argon2 won the Password Hashing
    Competition); the salting-and-slowness principle is the same.

Why a fresher should care:
    Databases leak. When one does, the difference between "salted scrypt" and "one round
    of SHA-256" is the difference between attackers getting nothing and attackers
    cracking most accounts overnight. This is a place where using the right tool is the
    whole job.

What this demo shows:
    Hashing the same password twice produces two different stored values, because each
    gets a fresh random salt, and verification still succeeds against both. Then a fast
    unsalted SHA-256 of the same password is shown giving one fixed value: identical for
    every user, and cheap to attack.

Run:  poetry run python demo_password_hash.py
"""

from __future__ import annotations

import hashlib
import hmac
import os

# scrypt cost parameters. Higher n means slower and more memory, so harder to attack.
_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> tuple[bytes, bytes]:
    """Return (salt, hash) using a fresh random salt and slow scrypt."""
    salt = os.urandom(16)  # unique per password, so equal passwords store differently
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return salt, digest


def verify_password(password: str, salt: bytes, expected: bytes) -> bool:
    """Recompute the hash with the stored salt and compare in constant time."""
    candidate = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    # compare_digest avoids leaking, through timing, how many bytes matched.
    return hmac.compare_digest(candidate, expected)


def unsafe_fast_hash(password: str) -> str:
    """UNSAFE: one round of SHA-256, no salt. Fast to compute means fast to crack."""
    return hashlib.sha256(password.encode()).hexdigest()


def main() -> None:
    password = "correct horse battery staple"

    # Salted scrypt: same password, hashed twice, gives two different stored values.
    salt1, hash1 = hash_password(password)
    salt2, hash2 = hash_password(password)
    print("salted scrypt (same password, two stored hashes):")
    print(f"  hash #1 starts {hash1.hex()[:12]}...")
    print(f"  hash #2 starts {hash2.hex()[:12]}...")
    print(f"  the two stored hashes differ: {hash1 != hash2}")

    # Verification still works against each stored (salt, hash) pair.
    print(f"  verify correct password vs #1: {verify_password(password, salt1, hash1)}")
    print(f"  verify correct password vs #2: {verify_password(password, salt2, hash2)}")
    print(f"  verify wrong password vs #1:   {verify_password('wrong', salt1, hash1)}")

    # Fast unsalted hash: one fixed value for everyone with this password.
    print("\nunsafe fast unsalted SHA-256 (same password, same output every time):")
    print(f"  {unsafe_fast_hash(password)}")
    print("  identical for every user with this password, and cheap to brute-force")


if __name__ == "__main__":
    main()
