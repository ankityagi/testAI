"""In-memory repository for local development and tests."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional
from uuid import uuid4

from ..services.hashing import hash_question
from ..services.security import generate_token, hash_password, verify_password

SEED_DIR = Path(__file__).resolve().parent / "sql"


@dataclass
class ParentRecord:
    id: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChildRecord:
    id: str
    parent_id: str
    name: str
    birthdate: Optional[str]
    grade: Optional[int]
    zip: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QuestionRecord:
    id: str
    standard_ref: str
    subject: str
    grade: Optional[int]
    topic: Optional[str]
    sub_topic: Optional[str]
    difficulty: Optional[str]
    stem: str
    options: list[str]
    correct_answer: str
    rationale: Optional[str]
    source: Optional[str]
    hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AttemptRecord:
    id: str
    child_id: str
    question_id: str
    selected: str
    correct: bool
    time_spent_ms: int
    created_at: datetime = field(default_factory=datetime.utcnow)


class MemoryRepository:
    """Simple in-memory implementation to emulate Supabase interactions."""

    def __init__(self) -> None:
        self.parents: dict[str, ParentRecord] = {}
        self.parents_by_email: dict[str, ParentRecord] = {}
        self.children: dict[str, ChildRecord] = {}
        self.questions: dict[str, QuestionRecord] = {}
        self.attempts: list[AttemptRecord] = []
        self.tokens: dict[str, str] = {}  # token -> parent_id
        self.standards: list[dict[str, Any]] = []
        self.seen_question_hashes: defaultdict[str, set[str]] = defaultdict(set)
        self._load_seed_data()

    # ------------------------------------------------------------------
    # Parent auth helpers
    def create_parent(self, *, email: str, password: str) -> dict[str, Any]:
        if email in self.parents_by_email:
            raise ValueError("Parent already exists")
        parent_id = str(uuid4())
        password_hash = hash_password(password)
        record = ParentRecord(id=parent_id, email=email, password_hash=password_hash)
        self.parents[parent_id] = record
        self.parents_by_email[email] = record
        token = generate_token()
        self.tokens[token] = parent_id
        return {"parent": self._parent_to_dict(record), "token": token}

    def authenticate_parent(self, *, email: str, password: str) -> dict[str, Any]:
        record = self.parents_by_email.get(email)
        if record is None or not verify_password(password, record.password_hash):
            raise ValueError("Invalid credentials")
        token = generate_token()
        self.tokens[token] = record.id
        return {"parent": self._parent_to_dict(record), "token": token}

    def get_parent_by_token(self, token: str) -> Optional[dict[str, Any]]:
        parent_id = self.tokens.get(token)
        if parent_id is None:
            return None
        record = self.parents.get(parent_id)
        if record is None:
            return None
        return self._parent_to_dict(record)

    # ------------------------------------------------------------------
    # Children management
    def child_belongs_to_parent(self, child_id: str, parent_id: str) -> bool:
        child = self.children.get(child_id)
        return bool(child and child.parent_id == parent_id)

    def get_child(self, child_id: str) -> Optional[dict[str, Any]]:
        child = self.children.get(child_id)
        return self._child_to_dict(child) if child else None

    def list_children(self, parent_id: str) -> list[dict[str, Any]]:
        return [
            self._child_to_dict(child)
            for child in self.children.values()
            if child.parent_id == parent_id
        ]

    def create_child(self, parent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        child_id = str(uuid4())
        record = ChildRecord(
            id=child_id,
            parent_id=parent_id,
            name=payload["name"],
            birthdate=str(payload.get("birthdate")) if payload.get("birthdate") else None,
            grade=payload.get("grade"),
            zip=payload.get("zip"),
        )
        self.children[child_id] = record
        return self._child_to_dict(record)

    def update_child(self, child_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = self.children.get(child_id)
        if record is None:
            raise ValueError("Child not found")
        if "name" in payload:
            value = payload["name"]
            if value:
                record.name = value
        if "birthdate" in payload:
            record.birthdate = str(payload["birthdate"]) if payload["birthdate"] else None
        if "grade" in payload:
            record.grade = payload["grade"]
        if "zip" in payload:
            record.zip = payload["zip"]
        return self._child_to_dict(record)

    def delete_child(self, child_id: str) -> None:
        record = self.children.pop(child_id, None)
        if record is None:
            raise ValueError("Child not found")
        self.seen_question_hashes.pop(child_id, None)
        self.attempts = [attempt for attempt in self.attempts if attempt.child_id != child_id]

    # ------------------------------------------------------------------
    # Standards
    def list_standards(self) -> list[dict[str, Any]]:
        return self.standards

    # ------------------------------------------------------------------
    # Questions & attempts
    def list_child_attempts(self, child_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": attempt.id,
                "child_id": attempt.child_id,
                "question_id": attempt.question_id,
                "selected": attempt.selected,
                "correct": attempt.correct,
                "time_spent_ms": attempt.time_spent_ms,
                "created_at": attempt.created_at.isoformat(),
            }
            for attempt in self.attempts
            if attempt.child_id == child_id
        ]

    def list_seen_question_hashes(self, child_id: str) -> list[str]:
        return list(self.seen_question_hashes.get(child_id, set()))

    def list_questions(
        self,
        *,
        subject: str,
        topic: Optional[str] = None,
        grade: Optional[int] = None,
        subtopic: Optional[str] = None,
        difficulties: Iterable[str] | None = None,
        exclude_hashes: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        difficulties_set = {d for d in (difficulties or []) if d}
        exclude = set(exclude_hashes or [])
        results: list[QuestionRecord] = []
        for record in self.questions.values():
            if record.subject != subject:
                continue
            if topic and record.topic != topic:
                continue
            if grade is not None and record.grade not in (None, grade):
                continue
            if subtopic is not None and record.sub_topic != subtopic:
                continue
            if difficulties_set and (record.difficulty or "easy") not in difficulties_set:
                continue
            if record.hash in exclude:
                continue
            results.append(record)
        results.sort(key=lambda q: q.created_at)
        return [self._question_to_dict(record) for record in results]

    def count_questions(
        self,
        *,
        subject: str,
        topic: Optional[str] = None,
        grade: Optional[int] = None,
        subtopic: Optional[str] = None,
    ) -> int:
        return len(
            self.list_questions(subject=subject, topic=topic, grade=grade, subtopic=subtopic)
        )

    def insert_questions(self, questions: list[dict[str, Any]]) -> None:
        for payload in questions:
            stem = payload["stem"]
            options = payload["options"]
            answer = payload["correct_answer"]
            question_hash = payload.get("hash") or hash_question(stem, options, answer)
            if any(q.hash == question_hash for q in self.questions.values()):
                continue
            record = QuestionRecord(
                id=payload.get("id", str(uuid4())),
                standard_ref=payload.get("standard_ref", ""),
                subject=payload.get("subject", "math"),
                grade=payload.get("grade"),
                topic=payload.get("topic"),
                sub_topic=payload.get("sub_topic"),
                difficulty=payload.get("difficulty"),
                stem=stem,
                options=list(options),
                correct_answer=answer,
                rationale=payload.get("rationale"),
                source=payload.get("source"),
                hash=question_hash,
            )
            self.questions[record.id] = record

    def fetch_questions(
        self,
        *,
        child_id: str,
        subject: str,
        topic: Optional[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        child = self.children.get(child_id)
        if child is None:
            raise ValueError("Unknown child")
        questions = self.list_questions(
            subject=subject,
            topic=topic,
            grade=child.grade,
            exclude_hashes=self.seen_question_hashes[child_id],
        )
        return questions[:limit]

    def log_attempt(
        self,
        *,
        child_id: str,
        question_id: str,
        selected: str,
        time_spent_ms: int,
    ) -> dict[str, Any]:
        question = self.questions.get(question_id)
        if question is None:
            raise ValueError("Unknown question")
        correct = selected == question.correct_answer
        attempt = AttemptRecord(
            id=str(uuid4()),
            child_id=child_id,
            question_id=question_id,
            selected=selected,
            correct=correct,
            time_spent_ms=time_spent_ms,
        )
        self.attempts.append(attempt)
        if correct:
            self.seen_question_hashes[child_id].add(question.hash)
        return {
            "attempt_id": attempt.id,
            "correct": correct,
            "expected": question.correct_answer,
        }

    def child_progress(self, child_id: str) -> dict[str, Any]:
        attempts = [a for a in self.attempts if a.child_id == child_id]
        total = len(attempts)
        correct = sum(1 for a in attempts if a.correct)
        accuracy = (correct / total) if total else 0.0
        streak = 0
        for attempt in reversed(attempts):
            if attempt.correct:
                streak += 1
            else:
                break
        by_subject: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {"correct": 0, "total": 0})
        for attempt in attempts:
            question = self.questions.get(attempt.question_id)
            if not question:
                continue
            stats = by_subject[question.subject]
            stats["total"] += 1
            if attempt.correct:
                stats["correct"] += 1
        normalized_subjects: dict[str, dict[str, Any]] = {}
        for subject, subject_stats in by_subject.items():
            total_subject = subject_stats["total"]
            accuracy_value = (
                subject_stats["correct"] / total_subject if total_subject else 0.0
            )
            normalized_subjects[subject] = {
                "correct": subject_stats["correct"],
                "total": total_subject,
                "accuracy": accuracy_value,
            }
        return {
            "attempted": total,
            "correct": correct,
            "accuracy": accuracy,
            "current_streak": streak,
            "by_subject": normalized_subjects,
        }

    # ------------------------------------------------------------------
    # Subtopics
    def insert_subtopics(self, subtopics: list[dict]) -> None:
        """Stub implementation - subtopics not supported in memory mode."""
        pass

    def list_subtopics(
        self,
        subject: str,
        grade: int | None = None,
        topic: str | None = None,
    ) -> list[dict]:
        """Stub implementation - returns empty list in memory mode."""
        return []

    def get_subtopic(self, subtopic_id: str) -> dict | None:
        """Stub implementation - subtopics not supported in memory mode."""
        return None

    def count_subtopics(self, *, subject: str, grade: int | None = None, topic: str | None = None) -> int:
        """Stub implementation - returns 0 in memory mode."""
        return 0

    # ------------------------------------------------------------------
    # Helpers
    def _load_seed_data(self) -> None:
        standards_path = SEED_DIR / "seed_standards.json"
        if standards_path.exists():
            self.standards = self._load_json(standards_path)
        questions_path = SEED_DIR / "seed_questions.json"
        if questions_path.exists():
            raw_questions = self._load_json(questions_path)
            self.insert_questions(raw_questions)

    def _load_json(self, path: Path) -> list[dict[str, Any]]:
        import json

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _parent_to_dict(record: ParentRecord) -> dict[str, Any]:
        return {"id": record.id, "email": record.email, "created_at": record.created_at.isoformat()}

    @staticmethod
    def _child_to_dict(record: ChildRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "parent_id": record.parent_id,
            "name": record.name,
            "birthdate": record.birthdate,
            "grade": record.grade,
            "zip": record.zip,
            "created_at": record.created_at.isoformat(),
        }

    @staticmethod
    def _question_to_dict(record: QuestionRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "standard_ref": record.standard_ref,
            "subject": record.subject,
            "grade": record.grade,
            "topic": record.topic,
            "sub_topic": record.sub_topic,
            "difficulty": record.difficulty,
            "stem": record.stem,
            "options": record.options,
            "correct_answer": record.correct_answer,
            "rationale": record.rationale,
            "source": record.source,
            "hash": record.hash,
        }


def build_memory_repository() -> MemoryRepository:
    return MemoryRepository()
