"""Stable hashing utilities for questions."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_question(stem: str, options: list[str], answer: str) -> str:
    payload = json.dumps({"stem": stem, "options": options, "answer": answer}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
