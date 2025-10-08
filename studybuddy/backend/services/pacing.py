"""Grade and ZIP-based pacing heuristics backed by seeded presets."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PRESET_PATH = Path(__file__).resolve().parents[1] / "db" / "sql" / "seed_pacing.json"


def _load_presets() -> list[dict[str, Any]]:
    if not PRESET_PATH.exists():
        return []
    with PRESET_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


PRESETS = _load_presets()


def current_month_index(reference: datetime | None = None) -> int:
    return (reference or datetime.utcnow()).month


def suggest_topics(
    grade: int,
    zip_code: str,
    *,
    subject: str | None = None,
    reference: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return pacing preset entries filtered by grade/subject/month."""
    month = current_month_index(reference)
    candidates = [entry for entry in PRESETS if entry.get("grade") == grade]
    month_filtered = [entry for entry in candidates if entry.get("month") in (None, month)]
    if month_filtered:
        candidates = month_filtered
    if subject:
        candidates = [entry for entry in candidates if entry.get("subject") == subject]
    return candidates


def first_topic_or_default(
    grade: int,
    subject: str,
    default: str | None = None,
    reference: datetime | None = None,
) -> str | None:
    entries = suggest_topics(grade, zip_code="", subject=subject, reference=reference)
    for entry in entries:
        topics = entry.get("topics") or []
        if topics:
            return topics[0]
    return default
