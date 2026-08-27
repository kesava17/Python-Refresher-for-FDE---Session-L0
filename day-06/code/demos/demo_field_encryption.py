"""Field encryption at rest (security): encrypt the column, keep the key elsewhere.

The concept, in plain words:
    Some fields are sensitive even inside your own database: a reviewer's email, a phone
    number, a national id. Encrypting the field means the stored value is unreadable
    ciphertext, so a leaked database backup or a curious DBA sees nothing useful. Your
    app decrypts on the way out with a key that is NOT kept next to the data. Fernet
    (from the cryptography library) is a safe, easy building block: it handles the
    algorithm choices for you and refuses to decrypt tampered data.

    In production the key itself is not hard-coded. It comes from a Key Management
    Service (KMS) at runtime, and a common pattern is envelope encryption: the KMS holds
    a master key that encrypts the per-record data key, so the key that touches your
    data is itself protected and can be rotated without re-encrypting everything.

Why a fresher should care:
    "The database is behind a firewall" is not encryption. Backups get copied, laptops
    get lost, and access gets over-granted. Encrypting the sensitive field, with the key
    held apart from the data, is what actually protects it when the storage leaks.

What this demo shows:
    A sensitive field is encrypted, the stored ciphertext is shown to be unreadable, and
    it decrypts back to the exact original. A comment marks where the key would come
    from a KMS rather than being generated in the process.

Run:  poetry run python demo_field_encryption.py
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


def main() -> None:
    # In production this key comes from a KMS at runtime (envelope encryption):
    # the KMS decrypts a stored data key for us. Here we generate one to keep the
    # demo self-contained.
    key = Fernet.generate_key()
    cipher = Fernet(key)

    sensitive_email = "reviewer.priya@example.com"
    print(f"original field:   {sensitive_email}")

    # Encrypt on the way in. The stored value is opaque bytes.
    stored = cipher.encrypt(sensitive_email.encode())
    print(f"stored ciphertext (unreadable): {stored[:24].decode()}...")
    print(f"  plaintext present in ciphertext? {b'example.com' in stored}")

    # Decrypt on the way out, back to the exact original.
    recovered = cipher.decrypt(stored).decode()
    print(f"decrypted field:  {recovered}")
    print(f"  round trip matches original: {recovered == sensitive_email}")

    # Tampering is rejected: change one byte and Fernet refuses to decrypt.
    tampered = stored[:-1] + bytes([stored[-1] ^ 0x01])
    try:
        cipher.decrypt(tampered)
        print("  tampered ciphertext decrypted (should not happen)")
    except InvalidToken:
        print("  tampered ciphertext is rejected, not silently accepted")


if __name__ == "__main__":
    main()
