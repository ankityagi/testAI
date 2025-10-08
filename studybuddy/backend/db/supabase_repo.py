"""Supabase-backed repository implementation."""
from __future__ import annotations

import os
from typing import Iterable

from supabase import Client, create_client

from ..services.hashing import hash_question
from ..services.security import generate_token, hash_password, verify_password


def _client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase credentials not configured")
    return create_client(url, key)


class SupabaseRepository:
    """PostgREST-backed repository leveraging Supabase tables."""

    def __init__(self, client: Client | None = None) -> None:
        self.client = client or _client()

    # ------------------------------------------------------------------
    # Parent authentication
    def create_parent(self, *, email: str, password: str) -> dict:
        existing = self.client.table("parents").select("id").eq("email", email).execute()
        if existing.data:
            raise ValueError("Parent already exists")
        password_hash = hash_password(password)
        inserted = (
            self.client.table("parents")
            .insert({"email": email, "password_hash": password_hash})
            .execute()
        )
        parent = inserted.data[0]
        token = generate_token()
        self.client.table("parent_tokens").insert({"token": token, "parent_id": parent["id"]}).execute()
        parent.pop("password_hash", None)
        return {"parent": parent, "token": token}

    def authenticate_parent(self, *, email: str, password: str) -> dict:
        result = (
            self.client
            .table("parents")
            .select("id,email,password_hash,created_at")
            .eq("email", email)
            .single()
            .execute()
        )
        parent = result.data
        if parent is None or not verify_password(password, parent.get("password_hash", "")):
            raise ValueError("Invalid credentials")
        token = generate_token()
        self.client.table("parent_tokens").insert({"token": token, "parent_id": parent["id"]}).execute()
        parent.pop("password_hash", None)
        return {"parent": parent, "token": token}

    def get_parent_by_token(self, token: str):
        result = (
            self.client
            .from_("parent_tokens")
            .select("parent_id, parents(id,email,created_at)")
            .eq("token", token)
            .maybe_single()
            .execute()
        )
        record = result.data
        if not record:
            return None
        parent = record.get("parents")
        if parent:
            return parent
        parent_id = record.get("parent_id")
        if not parent_id:
            return None
        parent_result = (
            self.client.table("parents")
            .select("id,email,created_at")
            .eq("id", parent_id)
            .maybe_single()
            .execute()
        )
        return parent_result.data

    # ------------------------------------------------------------------
    # Children
    def child_belongs_to_parent(self, child_id: str, parent_id: str) -> bool:
        res = (
            self.client.table("children")
            .select("id")
            .eq("id", child_id)
            .eq("parent_id", parent_id)
            .maybe_single()
            .execute()
        )
        return bool(res.data)

    def get_child(self, child_id: str) -> dict | None:
        res = (
            self.client.table("children")
            .select("*")
            .eq("id", child_id)
            .maybe_single()
            .execute()
        )
        return res.data

    def list_children(self, parent_id: str) -> list[dict]:
        res = (
            self.client.table("children")
            .select("*")
            .eq("parent_id", parent_id)
            .order("created_at")
            .execute()
        )
        return res.data or []

    def create_child(self, parent_id: str, payload: dict) -> dict:
        payload = {**payload, "parent_id": parent_id}
        inserted = self.client.table("children").insert(payload).execute()
        return inserted.data[0]

    def update_child(self, child_id: str, payload: dict) -> dict:
        if not payload:
            result = (
                self.client.table("children")
                .select("*")
                .eq("id", child_id)
                .single()
                .execute()
            )
            if not result.data:
                raise ValueError("Child not found")
            return result.data
        updated = (
            self.client.table("children")
            .update(payload)
            .eq("id", child_id)
            .execute()
        )
        if not updated.data:
            raise ValueError("Child not found")
        return updated.data[0]

    def delete_child(self, child_id: str) -> None:
        response = self.client.table("children").delete().eq("id", child_id).execute()
        if response.data is not None and not response.data:
            raise ValueError("Child not found")
        self.client.table("attempts").delete().eq("child_id", child_id).execute()
        self.client.table("seen_questions").delete().eq("child_id", child_id).execute()

    # ------------------------------------------------------------------
    # Standards & questions
    def list_standards(self) -> list[dict]:
        res = self.client.table("standards").select("*").order("grade").execute()
        return res.data or []

    def list_child_attempts(self, child_id: str) -> list[dict]:
        res = (
            self.client.table("attempts")
            .select("*")
            .eq("child_id", child_id)
            .order("created_at")
            .execute()
        )
        return res.data or []

    def list_seen_question_hashes(self, child_id: str) -> list[str]:
        res = (
            self.client.table("seen_questions")
            .select("question_hash")
            .eq("child_id", child_id)
            .execute()
        )
        return [row["question_hash"] for row in (res.data or [])]

    def list_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
        difficulties: Iterable[str] | None = None,
        exclude_hashes: Iterable[str] | None = None,
    ) -> list[dict]:
        query = self.client.table("question_bank").select("*").eq("subject", subject)
        if topic:
            query = query.eq("topic", topic)
        if grade is not None:
            query = query.or_(f"grade.eq.{grade},grade.is.null")
        if difficulties:
            collection = [d for d in difficulties if d]
            if collection:
                query = query.in_("difficulty", collection)
        if exclude_hashes:
            hashes = [h for h in exclude_hashes]
            if hashes:
                query = query.not_.in_("hash", hashes)
        res = query.order("created_at").execute()
        return res.data or []

    def count_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
    ) -> int:
        query = self.client.table("question_bank").select("id", count="exact").eq("subject", subject)
        if topic:
            query = query.eq("topic", topic)
        if grade is not None:
            query = query.eq("grade", grade)
        res = query.execute()
        return res.count or 0

    def insert_questions(self, questions: list[dict]) -> None:
        for question in questions:
            options = question["options"]
            answer = question["correct_answer"]
            stem = question["stem"]
            question_hash = question.get("hash") or hash_question(stem, options, answer)
            existing = (
                self.client.table("question_bank")
                .select("id")
                .eq("hash", question_hash)
                .maybe_single()
                .execute()
            )
            if existing.data:
                continue
            payload = {**question, "hash": question_hash}
            payload.setdefault("id", os.urandom(16).hex())
            self.client.table("question_bank").insert(payload).execute()

    # ------------------------------------------------------------------
    # Compatibility helpers for existing API
    def fetch_questions(
        self,
        *,
        child_id: str,
        subject: str,
        topic: str | None,
        limit: int,
    ) -> list[dict]:
        hashes = self.list_seen_question_hashes(child_id)
        questions = self.list_questions(
            subject=subject,
            topic=topic,
            grade=None,
            difficulties=None,
            exclude_hashes=hashes,
        )
        return questions[:limit]

    def log_attempt(
        self,
        *,
        child_id: str,
        question_id: str,
        selected: str,
        time_spent_ms: int,
    ) -> dict:
        question = (
            self.client.table("question_bank")
            .select("correct_answer,hash")
            .eq("id", question_id)
            .maybe_single()
            .execute()
            .data
        )
        if not question:
            raise ValueError("Unknown question")
        correct_answer = question["correct_answer"]
        correct = selected == correct_answer
        inserted = (
            self.client.table("attempts")
            .insert(
                {
                    "child_id": child_id,
                    "question_id": question_id,
                    "selected": selected,
                    "correct": correct,
                    "time_spent_ms": time_spent_ms,
                }
            )
            .execute()
        )
        if correct:
            self.client.table("seen_questions").upsert(
                {"child_id": child_id, "question_hash": question["hash"]}
            ).execute()
        attempt = inserted.data[0]
        return {
            "attempt_id": attempt["id"],
            "correct": correct,
            "expected": correct_answer,
        }

    def child_progress(self, child_id: str) -> dict:
        attempts = self.list_child_attempts(child_id)
        if not attempts:
            return {"attempted": 0, "correct": 0, "accuracy": 0.0, "current_streak": 0, "by_subject": {}}
        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt.get("correct"))
        accuracy = correct / total if total else 0.0
        streak = 0
        for attempt in reversed(attempts):
            if attempt.get("correct"):
                streak += 1
            else:
                break
        by_subject: dict[str, dict[str, float]] = {}
        question_ids = {attempt["question_id"] for attempt in attempts}
        question_rows = (
            self.client.table("question_bank")
            .select("id,subject")
            .in_("id", list(question_ids))
            .execute()
        ).data or []
        subject_map = {row["id"]: row["subject"] for row in question_rows}
        for attempt in attempts:
            subject = subject_map.get(attempt["question_id"], "unknown")
            stats = by_subject.setdefault(subject, {"correct": 0, "total": 0})
            stats["total"] += 1
            if attempt.get("correct"):
                stats["correct"] += 1
        for subject, stats in by_subject.items():
            total_subject = stats["total"]
            stats["accuracy"] = stats["correct"] / total_subject if total_subject else 0.0
        return {
            "attempted": total,
            "correct": correct,
            "accuracy": accuracy,
            "current_streak": streak,
            "by_subject": by_subject,
        }


def build_supabase_repository() -> SupabaseRepository:
    return SupabaseRepository()


__all__ = ["SupabaseRepository", "build_supabase_repository"]
