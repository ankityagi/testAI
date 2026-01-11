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


@dataclass
class QuizSessionRecord:
    id: str
    child_id: str
    subject: str
    topic: str
    subtopic: Optional[str]
    status: str  # 'active', 'completed', 'expired'
    duration_sec: int
    difficulty_mix_config: dict[str, Any]
    started_at: datetime
    submitted_at: Optional[datetime] = None
    score: Optional[int] = None
    total_questions: int = 0
    created_at: Optional[datetime] = None


@dataclass
class QuizSessionQuestionRecord:
    id: str
    quiz_session_id: str
    question_id: str
    index: int
    correct_choice: str
    explanation: str
    selected_choice: Optional[str] = None
    is_correct: Optional[bool] = None


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
        self.quiz_sessions: dict[str, QuizSessionRecord] = {}
        self.quiz_session_questions: list[QuizSessionQuestionRecord] = []
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

    def insert_standard(self, subject: str, grade: int, domain: str, sub_domain: str,
                       standard_ref: str, title: str, description: str) -> None:
        """Insert a single standard into memory."""
        # Check if standard already exists
        existing = any(s.get("standard_ref") == standard_ref for s in self.standards)
        if existing:
            print(f"[INSERT_STANDARD] Standard {standard_ref} already exists, skipping")
            return

        standard = {
            "id": len(self.standards) + 1,
            "subject": subject,
            "grade": grade,
            "domain": domain,
            "sub_domain": sub_domain,
            "standard_ref": standard_ref,
            "title": title,
            "description": description
        }
        self.standards.append(standard)

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
    # Recent questions (for quiz repeat reduction)
    def list_recent_question_hashes(self, child_id: str, limit: int = 30) -> list[str]:
        """Get question hashes from recent attempts (for repeat reduction window)."""
        # Get child's attempts sorted by newest first
        child_attempts = [
            a for a in sorted(self.attempts, key=lambda x: x.created_at, reverse=True)
            if a.child_id == child_id
        ]

        # Get hashes from most recent N attempts
        recent_hashes = []
        seen = set()
        for attempt in child_attempts[:limit]:
            question = self.questions.get(attempt.question_id)
            if question and question.hash not in seen:
                recent_hashes.append(question.hash)
                seen.add(question.hash)

        return recent_hashes

    # ------------------------------------------------------------------
    # Quiz Sessions
    def create_quiz_session(
        self, *,
        child_id: str,
        subject: str,
        topic: str,
        subtopic: str | None,
        question_count: int,
        duration_sec: int,
        difficulty_mix: dict
    ) -> dict:
        """Create a new quiz session."""
        session_id = str(uuid4())
        now = datetime.utcnow()
        record = QuizSessionRecord(
            id=session_id,
            child_id=child_id,
            subject=subject,
            topic=topic,
            subtopic=subtopic,
            status="active",
            duration_sec=duration_sec,
            difficulty_mix_config=difficulty_mix,
            started_at=now,
            total_questions=question_count,
            created_at=now,
        )
        self.quiz_sessions[session_id] = record
        return self._quiz_session_to_dict(record)

    def get_quiz_session(self, session_id: str) -> dict | None:
        """Get a quiz session by ID."""
        record = self.quiz_sessions.get(session_id)
        return self._quiz_session_to_dict(record) if record else None

    def list_quiz_sessions(self, child_id: str, limit: int = 20, offset: int = 0) -> list[dict]:
        """List quiz sessions for a child."""
        sessions = [
            s for s in self.quiz_sessions.values()
            if s.child_id == child_id
        ]
        # Sort by started_at descending
        sessions.sort(key=lambda x: x.started_at, reverse=True)
        return [self._quiz_session_to_dict(s) for s in sessions[offset:offset + limit]]

    def check_active_quiz(self, child_id: str, subject: str, topic: str) -> dict | None:
        """Check if child has an active quiz for the given subject/topic."""
        for session in self.quiz_sessions.values():
            if (session.child_id == child_id and
                session.subject == subject and
                session.topic == topic and
                session.status == "active"):
                return self._quiz_session_to_dict(session)
        return None

    def create_quiz_session_questions(self, session_id: str, questions: list[dict]) -> list[dict]:
        """Create quiz session questions."""
        created = []
        for q in questions:
            record = QuizSessionQuestionRecord(
                id=str(uuid4()),
                quiz_session_id=session_id,
                question_id=q["question_id"],
                index=q["index"],
                correct_choice=q["correct_choice"],
                explanation=q.get("explanation", ""),
            )
            self.quiz_session_questions.append(record)
            created.append(self._quiz_session_question_to_dict(record))
        return created

    def get_quiz_session_questions(self, session_id: str) -> list[dict]:
        """Get all questions for a quiz session with full question details."""
        session_questions = [
            q for q in self.quiz_session_questions
            if q.quiz_session_id == session_id
        ]
        session_questions.sort(key=lambda x: x.index)

        # Join with full question data
        result = []
        for sq in session_questions:
            question = self.questions.get(sq.question_id)
            if question:
                result.append({
                    **self._quiz_session_question_to_dict(sq),
                    "stem": question.stem,
                    "options": question.options,
                    "subject": question.subject,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                })
        return result

    def submit_quiz_session(self, session_id: str, answers: list[dict]) -> dict:
        """Submit answers for a quiz session."""
        # Update quiz session questions with answers
        for answer in answers:
            for sq in self.quiz_session_questions:
                if sq.quiz_session_id == session_id and sq.question_id == answer["question_id"]:
                    sq.selected_choice = answer.get("selected_choice", "")
                    sq.is_correct = answer.get("is_correct", False)

        # Calculate score
        session_questions = [q for q in self.quiz_session_questions if q.quiz_session_id == session_id]
        correct_count = sum(1 for q in session_questions if q.is_correct)
        total = len(session_questions)
        score = round((correct_count / total) * 100) if total > 0 else 0

        # Update session
        session = self.quiz_sessions.get(session_id)
        if session:
            session.status = "completed"
            session.submitted_at = datetime.utcnow()
            session.score = score
            return self._quiz_session_to_dict(session)
        return {}

    def expire_quiz_session(self, session_id: str) -> dict | None:
        """Mark a quiz session as expired."""
        session = self.quiz_sessions.get(session_id)
        if session:
            session.status = "expired"
            return self._quiz_session_to_dict(session)
        return None

    # upsert_question method - used by quiz_selection for generated questions
    def upsert_question(self, question: dict) -> dict:
        """Insert or update a question."""
        q_id = question.get("id") or str(uuid4())
        record = QuestionRecord(
            id=q_id,
            standard_ref=question.get("standard_ref", ""),
            subject=question.get("subject", ""),
            grade=question.get("grade"),
            topic=question.get("topic"),
            sub_topic=question.get("subtopic"),
            difficulty=question.get("difficulty"),
            stem=question.get("stem", ""),
            options=question.get("options", []),
            correct_answer=question.get("correct_answer", ""),
            rationale=question.get("rationale", ""),
            source=question.get("source", "generated"),
            hash=question.get("hash", ""),
        )
        self.questions[q_id] = record
        return self._question_to_dict(record)

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

    @staticmethod
    def _quiz_session_to_dict(record: QuizSessionRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "child_id": record.child_id,
            "subject": record.subject,
            "topic": record.topic,
            "subtopic": record.subtopic,
            "status": record.status,
            "duration_sec": record.duration_sec,
            "difficulty_mix_config": record.difficulty_mix_config,
            "started_at": record.started_at.isoformat() + "Z",
            "submitted_at": record.submitted_at.isoformat() + "Z" if record.submitted_at else None,
            "score": record.score,
            "total_questions": record.total_questions,
            "created_at": record.created_at.isoformat() + "Z" if record.created_at else record.started_at.isoformat() + "Z",
        }

    @staticmethod
    def _quiz_session_question_to_dict(record: QuizSessionQuestionRecord) -> dict[str, Any]:
        return {
            "id": record.id,
            "quiz_session_id": record.quiz_session_id,
            "question_id": record.question_id,
            "index": record.index,
            "correct_choice": record.correct_choice,
            "explanation": record.explanation,
            "selected_choice": record.selected_choice,
            "is_correct": record.is_correct,
        }


def build_memory_repository() -> MemoryRepository:
    return MemoryRepository()
