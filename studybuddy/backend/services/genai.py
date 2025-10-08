"""OpenAI-powered (or mocked) MCQ generator."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Iterable
from uuid import uuid4

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .hashing import hash_question
from .validators import QuestionValidationError, validate_mcq


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MOCK_MODE = os.getenv("STUDYBUDDY_MOCK_AI", "0") == "1"


@dataclass
class GenerationContext:
    subject: str
    topic: str | None
    grade: int | None
    difficulty: str
    count: int


def _build_prompt(ctx: GenerationContext) -> str:
    topic_text = ctx.topic or "grade-level concept"
    grade_text = f"Grade {ctx.grade}" if ctx.grade is not None else "Elementary"
    return (
        f"Generate {ctx.count} multiple-choice questions for {grade_text} students "
        f"learning {ctx.subject}. Focus on {topic_text}. Each question must include exactly four answer options, "
        f"one marked correct, a short rationale, a Common Core style topic tag, and a difficulty of {ctx.difficulty}. "
        "Respond with JSON array where each item has keys: stem, options (array of four strings), correct_answer, "
        "rationale, subject, grade, topic, sub_topic, difficulty."
    )


def _mock_questions(ctx: GenerationContext) -> list[dict[str, Any]]:
    """Deterministic fallback when OpenAI is unavailable."""
    base_topic = ctx.topic or f"core {ctx.subject}"
    questions: list[dict[str, Any]] = []
    for index in range(ctx.count):
        stem = (
            f"[{ctx.difficulty.title()}] {base_topic.title()} practice {index + 1}: "
            f"What is the best answer for {ctx.subject} learners?"
        )
        options = [
            f"Choice {chr(65 + i)} for {base_topic}" for i in range(4)
        ]
        correct_answer = options[index % 4]
        question = {
            "id": str(uuid4()),
            "subject": ctx.subject,
            "grade": ctx.grade,
            "topic": base_topic,
            "sub_topic": base_topic,
            "difficulty": ctx.difficulty,
            "stem": stem,
            "options": options,
            "correct_answer": correct_answer,
            "rationale": f"Because {correct_answer} best fits the prompt.",
            "source": "mock",
        }
        question["hash"] = hash_question(question["stem"], question["options"], question["correct_answer"])
        questions.append(question)
    return questions


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=api_key)


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
def _invoke_openai(prompt: str, *, model: str) -> str:
    client = _client()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "You create Common Core-aligned multiple-choice questions in strict JSON."
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = response.output[0].content[0].text  # type: ignore[attr-defined]
    return content


def _parse_questions(raw: str) -> Iterable[dict[str, Any]]:
    payload = json.loads(raw)
    if isinstance(payload, dict) and "questions" in payload:
        payload = payload["questions"]
    if not isinstance(payload, list):
        raise QuestionValidationError("Expected a JSON array of questions")
    return payload


def generate_mcqs(*, context: GenerationContext) -> list[dict[str, Any]]:
    """Generate or mock MCQs for the given context."""
    if MOCK_MODE:
        return _mock_questions(context)

    prompt = _build_prompt(context)
    try:
        raw = _invoke_openai(prompt, model=DEFAULT_MODEL)
        candidates = list(_parse_questions(raw))
    except Exception as exc:  # noqa: BLE001 - surface fallback gracefully
        if os.getenv("STUDYBUDDY_ALLOW_FALLBACK", "1") == "1":
            return _mock_questions(context)
        raise RuntimeError(f"Failed to generate MCQs: {exc}") from exc

    validated_questions: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            validate_mcq(candidate)
        except QuestionValidationError:
            continue
        stem = candidate["stem"]
        options = candidate["options"]
        answer = candidate["correct_answer"]
        candidate.setdefault("subject", context.subject)
        candidate.setdefault("grade", context.grade)
        candidate.setdefault("topic", context.topic or context.subject)
        candidate.setdefault("difficulty", context.difficulty)
        candidate.setdefault("source", "openai")
        candidate["hash"] = hash_question(stem, options, answer)
        candidate.setdefault("id", str(uuid4()))
        validated_questions.append(candidate)
    return validated_questions


__all__ = [
    "GenerationContext",
    "generate_mcqs",
]
