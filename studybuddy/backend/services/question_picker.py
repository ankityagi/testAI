"""Adaptive question selection and generation service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .genai import GenerationContext, generate_mcqs
from .hashing import hash_question

DIFFICULTY_ORDER = ["easy", "medium", "hard"]
MIN_STOCK_THRESHOLD = 10


@dataclass
class QuestionBatch:
    questions: list[dict]
    stock_deficit: int = 0


def _difficulty_sequence(attempts: Sequence[dict]) -> list[str]:
    if not attempts:
        return ["easy", "medium"]
    correct = sum(1 for attempt in attempts if attempt.get("correct"))
    accuracy = correct / len(attempts)
    if accuracy >= 0.85 and len(attempts) >= 5:
        return ["medium", "hard", "easy"]
    if accuracy >= 0.6:
        return ["easy", "medium", "hard"]
    return ["easy"]


def _normalise_question(question: dict, *, subject: str, topic: str | None, grade: int | None, difficulty: str) -> dict:
    question.setdefault("id", question.get("question_id"))
    question.setdefault("subject", subject)
    question.setdefault("topic", topic or subject)
    question.setdefault("difficulty", difficulty)
    question.setdefault("grade", grade)
    question.setdefault("source", question.get("source", "generated"))
    question.setdefault("options", question.get("options", []))
    question.setdefault("correct_answer", question.get("correct_answer"))
    question.setdefault("rationale", question.get("rationale", ""))
    options = question["options"]
    answer = question["correct_answer"]
    stem = question["stem"]
    question["hash"] = question.get("hash") or hash_question(stem, options, answer)
    return question


def _unique_questions(questions: Iterable[dict], seen_hashes: set[str]) -> list[dict]:
    unique: list[dict] = []
    for question in questions:
        if question["hash"] in seen_hashes:
            continue
        seen_hashes.add(question["hash"])
        unique.append(question)
    return unique


def fetch_batch(
    *,
    repo,
    child: dict,
    subject: str,
    topic: str | None,
    limit: int,
    generator=generate_mcqs,
) -> QuestionBatch:
    child_id = child["id"]
    attempts = repo.list_child_attempts(child_id)
    difficulty_preferences = _difficulty_sequence(attempts)
    seen_hashes = set(repo.list_seen_question_hashes(child_id))

    grade = child.get("grade")
    available_questions: list[dict] = []
    for difficulty in difficulty_preferences:
        fetched = repo.list_questions(
            subject=subject,
            topic=topic,
            grade=grade,
            difficulties=[difficulty],
            exclude_hashes=seen_hashes,
        )
        for question in fetched:
            question.setdefault("difficulty", difficulty)
        available_questions.extend(fetched)

    picked: list[dict] = []
    seen_for_session = set(seen_hashes)
    for question in available_questions:
        if len(picked) >= limit:
            break
        if question["hash"] in seen_for_session:
            continue
        seen_for_session.add(question["hash"])
        picked.append(question)

    deficit = max(limit - len(picked), 0)
    if deficit > 0:
        preferred_difficulty = difficulty_preferences[0]
        ctx = GenerationContext(
            subject=subject,
            topic=topic,
            grade=grade,
            difficulty=preferred_difficulty,
            count=deficit,
        )
        generated = [
            _normalise_question(item, subject=subject, topic=topic, grade=grade, difficulty=preferred_difficulty)
            for item in generator(context=ctx)
        ]
        generated = _unique_questions(generated, seen_for_session)
        if generated:
            repo.insert_questions(generated)
            picked.extend(generated[:deficit])

    stock_level = repo.count_questions(subject=subject, topic=topic, grade=grade)
    stock_deficit = max(MIN_STOCK_THRESHOLD - stock_level, 0)
    return QuestionBatch(questions=picked[:limit], stock_deficit=stock_deficit)


def top_up_stock(
    *,
    repo,
    child: dict,
    subject: str,
    topic: str | None,
    count: int,
    generator=generate_mcqs,
) -> None:
    grade = child.get("grade")
    ctx = GenerationContext(
        subject=subject,
        topic=topic,
        grade=grade,
        difficulty="medium",
        count=count,
    )
    generated = generator(context=ctx)
    normalised = [
        _normalise_question(item, subject=subject, topic=topic, grade=grade, difficulty=item.get("difficulty", "medium"))
        for item in generated
    ]
    repo.insert_questions(normalised)


__all__ = ["fetch_batch", "top_up_stock", "QuestionBatch"]
