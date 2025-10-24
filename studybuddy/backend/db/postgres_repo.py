"""Direct PostgreSQL repository implementation."""
from __future__ import annotations

import os
from typing import Iterable

import psycopg2
from psycopg2.extras import RealDictCursor

from ..services.hashing import hash_question
from ..services.security import generate_token, hash_password, verify_password


def _get_connection():
    url = os.environ.get("SUPABASE_URL")
    password = os.environ.get("SUPABASE_DB_PASSWORD")

    if not url or not password:
        raise RuntimeError("SUPABASE_URL and SUPABASE_DB_PASSWORD must be set")

    host = url.replace("https://", "").replace("http://", "").split("/")[0]
    project_ref = host.split(".")[0]

    conn_params = {
        "host": "aws-1-us-west-1.pooler.supabase.com",
        "port": 6543,
        "database": "postgres",
        "user": f"postgres.{project_ref}",
        "password": password,
    }

    import logging
    logging.warning(f"Connecting to {conn_params['host']}:{conn_params['port']} as {conn_params['user']}")

    return psycopg2.connect(**conn_params)


class PostgresRepository:
    """Direct PostgreSQL repository bypassing Supabase SDK."""

    def __init__(self):
        self.get_connection = _get_connection

    def create_parent(self, *, email: str, password: str) -> dict:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id FROM parents WHERE email = %s", (email,))
                if cur.fetchone():
                    raise ValueError("Parent already exists")

                password_hash = hash_password(password)
                cur.execute(
                    "INSERT INTO parents (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
                    (email, password_hash)
                )
                parent = dict(cur.fetchone())

                token = generate_token()
                cur.execute(
                    "INSERT INTO parent_tokens (token, parent_id) VALUES (%s, %s)",
                    (token, parent["id"])
                )
                conn.commit()

                return {"parent": parent, "token": token}
        finally:
            conn.close()

    def authenticate_parent(self, *, email: str, password: str) -> dict:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, email, password_hash, created_at FROM parents WHERE email = %s",
                    (email,)
                )
                parent = cur.fetchone()
                if not parent or not verify_password(password, parent.get("password_hash", "")):
                    raise ValueError("Invalid credentials")

                parent = dict(parent)
                parent.pop("password_hash", None)

                token = generate_token()
                cur.execute(
                    "INSERT INTO parent_tokens (token, parent_id) VALUES (%s, %s)",
                    (token, parent["id"])
                )
                conn.commit()

                return {"parent": parent, "token": token}
        finally:
            conn.close()

    def get_parent_by_token(self, token: str):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT parent_id FROM parent_tokens WHERE token = %s",
                    (token,)
                )
                record = cur.fetchone()
                if not record:
                    return None

                cur.execute(
                    "SELECT id, email, created_at FROM parents WHERE id = %s",
                    (record["parent_id"],)
                )
                parent = cur.fetchone()
                return dict(parent) if parent else None
        finally:
            conn.close()

    def child_belongs_to_parent(self, child_id: str, parent_id: str) -> bool:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id FROM children WHERE id = %s AND parent_id = %s",
                    (child_id, parent_id)
                )
                return cur.fetchone() is not None
        finally:
            conn.close()

    def get_child(self, child_id: str) -> dict | None:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM children WHERE id = %s", (child_id,))
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            conn.close()

    def list_children(self, parent_id: str) -> list[dict]:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM children WHERE parent_id = %s ORDER BY created_at",
                    (parent_id,)
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def create_child(self, parent_id: str, payload: dict) -> dict:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                payload = {**payload, "parent_id": parent_id}
                columns = ", ".join(payload.keys())
                placeholders = ", ".join(["%s"] * len(payload))
                cur.execute(
                    f"INSERT INTO children ({columns}) VALUES ({placeholders}) RETURNING *",
                    tuple(payload.values())
                )
                result = dict(cur.fetchone())
                conn.commit()
                return result
        finally:
            conn.close()

    def update_child(self, child_id: str, payload: dict) -> dict:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if not payload:
                    cur.execute("SELECT * FROM children WHERE id = %s", (child_id,))
                    result = cur.fetchone()
                    if not result:
                        raise ValueError("Child not found")
                    return dict(result)

                set_clause = ", ".join([f"{k} = %s" for k in payload.keys()])
                values = list(payload.values()) + [child_id]
                cur.execute(
                    f"UPDATE children SET {set_clause} WHERE id = %s RETURNING *",
                    values
                )
                result = cur.fetchone()
                if not result:
                    raise ValueError("Child not found")
                conn.commit()
                return dict(result)
        finally:
            conn.close()

    def delete_child(self, child_id: str) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM children WHERE id = %s RETURNING id", (child_id,))
                if not cur.fetchone():
                    raise ValueError("Child not found")
                cur.execute("DELETE FROM attempts WHERE child_id = %s", (child_id,))
                cur.execute("DELETE FROM seen_questions WHERE child_id = %s", (child_id,))
                conn.commit()
        finally:
            conn.close()

    def list_standards(self) -> list[dict]:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM standards ORDER BY grade")
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def list_child_attempts(self, child_id: str) -> list[dict]:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM attempts WHERE child_id = %s ORDER BY created_at",
                    (child_id,)
                )
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def list_seen_question_hashes(self, child_id: str) -> list[str]:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT question_hash FROM seen_questions WHERE child_id = %s",
                    (child_id,)
                )
                return [row["question_hash"] for row in cur.fetchall()]
        finally:
            conn.close()

    def list_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
        subtopic: str | None = None,
        difficulties: Iterable[str] | None = None,
        exclude_hashes: Iterable[str] | None = None,
    ) -> list[dict]:
        from ..services.text_utils import normalize_subject, normalize_topic, normalize_subtopic

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Normalize inputs before querying
                query = "SELECT * FROM question_bank WHERE subject = %s"
                params = [normalize_subject(subject)]

                # Exclude mock questions unless STUDYBUDDY_MOCK_AI is enabled
                mock_mode = os.getenv("STUDYBUDDY_MOCK_AI", "0") == "1"
                if not mock_mode:
                    query += " AND (source IS NULL OR source != 'mock')"

                if topic:
                    query += " AND topic = %s"
                    params.append(normalize_topic(topic))

                if grade is not None:
                    query += " AND (grade = %s OR grade IS NULL)"
                    params.append(grade)

                if subtopic is not None:
                    query += " AND sub_topic = %s"
                    params.append(normalize_subtopic(subtopic))

                if difficulties:
                    collection = [d for d in difficulties if d]
                    if collection:
                        placeholders = ", ".join(["%s"] * len(collection))
                        query += f" AND difficulty IN ({placeholders})"
                        params.extend(collection)

                if exclude_hashes:
                    hashes = [h for h in exclude_hashes]
                    if hashes:
                        placeholders = ", ".join(["%s"] * len(hashes))
                        query += f" AND hash NOT IN ({placeholders})"
                        params.extend(hashes)

                query += " ORDER BY RANDOM()"  # Randomize question order
                cur.execute(query, params)
                results = []
                for row in cur.fetchall():
                    question = dict(row)
                    # JSONB columns are automatically deserialized by psycopg2
                    results.append(question)
                return results
        finally:
            conn.close()

    def count_questions(
        self,
        *,
        subject: str,
        topic: str | None = None,
        grade: int | None = None,
        subtopic: str | None = None,
    ) -> int:
        from ..services.text_utils import normalize_subject, normalize_topic, normalize_subtopic

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Normalize inputs before querying
                query = "SELECT COUNT(*) as count FROM question_bank WHERE subject = %s"
                params = [normalize_subject(subject)]

                # Exclude mock questions unless STUDYBUDDY_MOCK_AI is enabled
                mock_mode = os.getenv("STUDYBUDDY_MOCK_AI", "0") == "1"
                if not mock_mode:
                    query += " AND (source IS NULL OR source != 'mock')"

                if topic:
                    query += " AND topic = %s"
                    params.append(normalize_topic(topic))

                if grade is not None:
                    query += " AND (grade = %s OR grade IS NULL)"
                    params.append(grade)

                if subtopic is not None:
                    query += " AND sub_topic = %s"
                    params.append(normalize_subtopic(subtopic))

                cur.execute(query, params)
                return cur.fetchone()["count"]
        finally:
            conn.close()

    def insert_questions(self, questions: list[dict]) -> None:
        import json
        from ..services.text_utils import normalize_metadata

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for question in questions:
                    options = question["options"]
                    answer = question["correct_answer"]
                    stem = question["stem"]
                    question_hash = question.get("hash") or hash_question(stem, options, answer)

                    cur.execute(
                        "SELECT id FROM question_bank WHERE hash = %s",
                        (question_hash,)
                    )
                    existing = cur.fetchone()
                    if existing:
                        # Update the question object with the existing database ID
                        question["id"] = existing["id"]
                        print(f"[INSERT_Q] Question already exists with id={existing['id']}, updating question object", flush=True)
                        continue

                    payload = {**question, "hash": question_hash}
                    payload.setdefault("id", os.urandom(16).hex())

                    # Normalize metadata (subject, topic, subtopic) to lowercase
                    normalize_metadata(payload)

                    # Convert options to JSON string for JSONB column
                    if "options" in payload and isinstance(payload["options"], list):
                        payload["options"] = json.dumps(payload["options"])

                    columns = ", ".join(payload.keys())
                    placeholders = ", ".join(["%s"] * len(payload))
                    cur.execute(
                        f"INSERT INTO question_bank ({columns}) VALUES ({placeholders})",
                        tuple(payload.values())
                    )
                    print(f"[INSERT_Q] Inserted new question with id={payload['id']} topic={payload['topic']} sub_topic={payload['sub_topic']} grade={payload['grade']} difficulty={payload['difficulty']}", flush=True)
                conn.commit()
        finally:
            conn.close()

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
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                print(f"[LOG_ATTEMPT] Looking for question_id: {question_id}", flush=True)
                cur.execute(
                    "SELECT correct_answer, hash FROM question_bank WHERE id = %s",
                    (question_id,)
                )
                question = cur.fetchone()
                if not question:
                    print(f"[LOG_ATTEMPT] Question not found in database: {question_id}", flush=True)
                    raise ValueError(f"Unknown question: {question_id}")

                correct_answer = question["correct_answer"]
                correct = selected == correct_answer

                cur.execute(
                    "INSERT INTO attempts (child_id, question_id, selected, correct, time_spent_ms) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (child_id, question_id, selected, correct, time_spent_ms)
                )
                attempt_id = cur.fetchone()["id"]

                if correct:
                    cur.execute(
                        "INSERT INTO seen_questions (child_id, question_hash) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (child_id, question["hash"])
                    )

                conn.commit()

                return {
                    "attempt_id": attempt_id,
                    "correct": correct,
                    "expected": correct_answer,
                }
        finally:
            conn.close()

    def child_progress(self, child_id: str) -> dict:
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM attempts WHERE child_id = %s ORDER BY created_at",
                    (child_id,)
                )
                attempts = [dict(row) for row in cur.fetchall()]

                if not attempts:
                    return {"attempted": 0, "correct": 0, "accuracy": 0, "current_streak": 0, "by_subject": {}}

                total = len(attempts)
                correct = sum(1 for attempt in attempts if attempt.get("correct"))
                # Convert to percentage and round to integer (0-100)
                accuracy = round((correct / total * 100)) if total else 0

                streak = 0
                for attempt in reversed(attempts):
                    if attempt.get("correct"):
                        streak += 1
                    else:
                        break

                question_ids = {attempt["question_id"] for attempt in attempts}
                placeholders = ", ".join(["%s"] * len(question_ids))
                cur.execute(
                    f"SELECT id, subject FROM question_bank WHERE id IN ({placeholders})",
                    list(question_ids)
                )
                subject_map = {row["id"]: row["subject"] for row in cur.fetchall()}

                by_subject: dict[str, dict[str, int]] = {}
                for attempt in attempts:
                    subject = subject_map.get(attempt["question_id"], "unknown")
                    # Capitalize subject name for consistency
                    subject = subject.capitalize() if subject else "Unknown"
                    stats = by_subject.setdefault(subject, {"correct": 0, "total": 0})
                    stats["total"] += 1
                    if attempt.get("correct"):
                        stats["correct"] += 1

                for subject, stats in by_subject.items():
                    total_subject = stats["total"]
                    # Convert to percentage and round to integer (0-100)
                    stats["accuracy"] = round((stats["correct"] / total_subject * 100)) if total_subject else 0

                return {
                    "attempted": total,
                    "correct": correct,
                    "accuracy": accuracy,
                    "current_streak": streak,
                    "by_subject": by_subject,
                }
        finally:
            conn.close()


    def insert_subtopics(self, subtopics: list[dict]) -> None:
        """Insert subtopics into the database."""
        from ..services.text_utils import normalize_metadata

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for subtopic in subtopics:
                    # Normalize metadata before insertion
                    normalized = {**subtopic}
                    normalize_metadata(normalized)

                    # Check if subtopic already exists
                    cur.execute(
                        "SELECT id FROM subtopics WHERE subject = %s AND grade = %s AND topic = %s AND subtopic = %s",
                        (normalized["subject"], normalized["grade"], normalized["topic"], normalized["subtopic"])
                    )
                    if cur.fetchone():
                        print(f"[INSERT_SUBTOPIC] Subtopic already exists: {normalized['subject']}/{normalized['grade']}/{normalized['topic']}/{normalized['subtopic']}", flush=True)
                        continue

                    # Insert new subtopic
                    cur.execute(
                        """INSERT INTO subtopics (subject, grade, topic, subtopic, description, sequence_order)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            normalized["subject"],
                            normalized["grade"],
                            normalized["topic"],
                            normalized["subtopic"],
                            normalized.get("description"),
                            normalized.get("sequence_order", 0)
                        )
                    )
                    print(f"[INSERT_SUBTOPIC] Inserted: {normalized['subject']}/{normalized['grade']}/{normalized['topic']}/{normalized['subtopic']}", flush=True)
                conn.commit()
        finally:
            conn.close()

    def list_subtopics(
        self,
        subject: str,
        grade: int | None = None,
        topic: str | None = None,
    ) -> list[dict]:
        """List subtopics filtered by subject, grade, and/or topic."""
        from ..services.text_utils import normalize_subject, normalize_topic

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Normalize inputs before querying
                query = "SELECT * FROM subtopics WHERE subject = %s"
                params = [normalize_subject(subject)]

                if grade is not None:
                    query += " AND grade = %s"
                    params.append(grade)

                if topic:
                    query += " AND topic = %s"
                    params.append(normalize_topic(topic))

                query += " ORDER BY sequence_order, subtopic"
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_subtopic(self, subtopic_id: str) -> dict | None:
        """Get a single subtopic by ID."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM subtopics WHERE id = %s", (subtopic_id,))
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            conn.close()

    def count_subtopics(self, *, subject: str, grade: int | None = None, topic: str | None = None) -> int:
        """Count subtopics filtered by subject, grade, and/or topic."""
        from ..services.text_utils import normalize_subject, normalize_topic

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Normalize inputs before querying
                query = "SELECT COUNT(*) as count FROM subtopics WHERE subject = %s"
                params = [normalize_subject(subject)]

                if grade is not None:
                    query += " AND grade = %s"
                    params.append(grade)

                if topic:
                    query += " AND topic = %s"
                    params.append(normalize_topic(topic))

                cur.execute(query, params)
                return cur.fetchone()["count"]
        finally:
            conn.close()

    # Session tracking methods
    def create_session(
        self,
        *,
        child_id: str,
        subject: str | None = None,
        topic: str | None = None,
        subtopic: str | None = None,
    ) -> dict:
        """Create a new practice session."""
        from ..services.text_utils import normalize_subject, normalize_topic, normalize_subtopic

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Normalize metadata before insertion
                normalized_subject = normalize_subject(subject) if subject else None
                normalized_topic = normalize_topic(topic) if topic else None
                normalized_subtopic = normalize_subtopic(subtopic) if subtopic else None

                cur.execute(
                    """INSERT INTO sessions (child_id, subject, topic, subtopic)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id, child_id, subject, topic, subtopic, started_at, ended_at, created_at, updated_at""",
                    (child_id, normalized_subject, normalized_topic, normalized_subtopic)
                )
                session = dict(cur.fetchone())
                conn.commit()
                return session
        finally:
            conn.close()

    def get_active_session(self, child_id: str) -> dict | None:
        """Get the active (not ended) session for a child, if any."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, child_id, subject, topic, subtopic, started_at, ended_at, created_at, updated_at
                       FROM sessions
                       WHERE child_id = %s AND ended_at IS NULL
                       ORDER BY started_at DESC
                       LIMIT 1""",
                    (child_id,)
                )
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            conn.close()

    def get_session(self, session_id: str) -> dict | None:
        """Get a session by ID."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, child_id, subject, topic, subtopic, started_at, ended_at, created_at, updated_at
                       FROM sessions
                       WHERE id = %s""",
                    (session_id,)
                )
                result = cur.fetchone()
                return dict(result) if result else None
        finally:
            conn.close()

    def end_session(self, session_id: str) -> dict:
        """End a session by setting ended_at timestamp."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """UPDATE sessions
                       SET ended_at = now()
                       WHERE id = %s AND ended_at IS NULL
                       RETURNING id, child_id, subject, topic, subtopic, started_at, ended_at, created_at, updated_at""",
                    (session_id,)
                )
                result = cur.fetchone()
                if not result:
                    raise ValueError(f"Session not found or already ended: {session_id}")
                conn.commit()
                return dict(result)
        finally:
            conn.close()

    def get_session_summary(self, session_id: str) -> dict:
        """Get summary statistics for a session."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get session details
                cur.execute(
                    """SELECT id, child_id, subject, topic, subtopic, started_at, ended_at, created_at, updated_at
                       FROM sessions WHERE id = %s""",
                    (session_id,)
                )
                session = cur.fetchone()
                if not session:
                    raise ValueError(f"Session not found: {session_id}")

                session = dict(session)

                # Get attempts within the session time window
                if session["ended_at"]:
                    cur.execute(
                        """SELECT a.*, q.subject
                           FROM attempts a
                           JOIN question_bank q ON a.question_id = q.id
                           WHERE a.child_id = %s
                             AND a.created_at >= %s
                             AND a.created_at <= %s
                           ORDER BY a.created_at""",
                        (session["child_id"], session["started_at"], session["ended_at"])
                    )
                else:
                    cur.execute(
                        """SELECT a.*, q.subject
                           FROM attempts a
                           JOIN question_bank q ON a.question_id = q.id
                           WHERE a.child_id = %s
                             AND a.created_at >= %s
                           ORDER BY a.created_at""",
                        (session["child_id"], session["started_at"])
                    )

                attempts = [dict(row) for row in cur.fetchall()]

                # Calculate statistics
                questions_attempted = len(attempts)
                questions_correct = sum(1 for a in attempts if a.get("correct"))
                accuracy = round((questions_correct / questions_attempted * 100)) if questions_attempted else 0
                total_time_ms = sum(a.get("time_spent_ms", 0) for a in attempts)
                avg_time_per_question_ms = total_time_ms // questions_attempted if questions_attempted else 0

                # Get unique subjects practiced
                subjects_practiced = list({a["subject"].capitalize() for a in attempts if a.get("subject")})

                return {
                    "session": session,
                    "questions_attempted": questions_attempted,
                    "questions_correct": questions_correct,
                    "accuracy": accuracy,
                    "total_time_ms": total_time_ms,
                    "avg_time_per_question_ms": avg_time_per_question_ms,
                    "subjects_practiced": subjects_practiced,
                }
        finally:
            conn.close()


def build_postgres_repository() -> PostgresRepository:
    return PostgresRepository()


__all__ = ["PostgresRepository", "build_postgres_repository"]
