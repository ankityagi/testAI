"""Repository factory to switch between Supabase and in-memory stores."""
from __future__ import annotations

import os
from typing import Iterable, Protocol

from .memory import MemoryRepository, build_memory_repository

try:
    from .postgres_repo import PostgresRepository, build_postgres_repository
except ImportError:
    PostgresRepository = None  # type: ignore[assignment]
    build_postgres_repository = None  # type: ignore[assignment]

try:  # pragma: no cover - optional import for Supabase mode
    from .supabase_repo import SupabaseRepository, build_supabase_repository
except ImportError:  # pragma: no cover
    SupabaseRepository = None  # type: ignore[assignment]
    build_supabase_repository = None  # type: ignore[assignment]


class Repository(Protocol):
    """Minimal protocol used by the routes for data persistence."""

    def create_parent(self, *, email: str, password: str) -> dict: ...

    def authenticate_parent(self, *, email: str, password: str) -> dict: ...

    def get_parent_by_token(self, token: str): ...

    def child_belongs_to_parent(self, child_id: str, parent_id: str) -> bool: ...

    def get_child(self, child_id: str) -> dict | None: ...

    def list_children(self, parent_id: str) -> list[dict]: ...

    def create_child(self, parent_id: str, payload: dict) -> dict: ...

    def update_child(self, child_id: str, payload: dict) -> dict: ...

    def delete_child(self, child_id: str) -> None: ...

    def list_standards(self) -> list[dict]: ...

    def list_child_attempts(self, child_id: str) -> list[dict]: ...

    def list_seen_question_hashes(self, child_id: str) -> list[str]: ...

    def list_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
        difficulties: Iterable[str] | None = None,
        exclude_hashes: Iterable[str] | None = None,
    ) -> list[dict]: ...

    def count_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
    ) -> int: ...

    def insert_questions(self, questions: list[dict]) -> None: ...

    def fetch_questions(
        self,
        *,
        child_id: str,
        subject: str,
        topic: str | None,
        limit: int,
    ) -> list[dict]: ...

    def log_attempt(
        self, *, child_id: str, question_id: str, selected: str, time_spent_ms: int
    ) -> dict: ...

    def child_progress(self, child_id: str) -> dict: ...


def build_repository() -> Repository:
    import logging
    logger = logging.getLogger(__name__)

    mode = os.getenv("STUDYBUDDY_DATA_MODE", "memory").lower()
    logger.warning(f"Building repository with mode: {mode}")

    if mode == "supabase":
        if build_postgres_repository is None:
            raise RuntimeError("PostgreSQL dependencies (psycopg2) are not installed")
        try:
            repo = build_postgres_repository()
            logger.warning(f"Successfully initialized PostgreSQL repository!")
            return repo
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL repository: {e}. Falling back to memory mode.")
            return build_memory_repository()

    logger.warning(f"Using memory repository")
    return build_memory_repository()


__all__ = ["Repository", "build_repository", "SupabaseRepository"]
