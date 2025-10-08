"""Security helpers for simple auth tokens."""
from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str) -> str:
    """Return a SHA256 hash for stored passwords."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash


def generate_token() -> str:
    return secrets.token_urlsafe(32)
