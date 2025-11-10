"""Pydantic schemas for request/response bodies."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str) -> str:
    if not EMAIL_PATTERN.fullmatch(value):
        raise ValueError("Invalid email address")
    return value


class Parent(BaseModel):
    id: str
    email: str
    created_at: datetime

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _validate_email(value)


class AuthRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _validate_email(value)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    parent: Parent


class ChildBase(BaseModel):
    name: str
    birthdate: Optional[date] = None
    grade: Optional[int] = Field(default=None, ge=0, le=12)
    zip: Optional[str] = None


class ChildCreate(ChildBase):
    pass


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[date] = None
    grade: Optional[int] = Field(default=None, ge=0, le=12)
    zip: Optional[str] = None


class Child(ChildBase):
    id: str
    parent_id: str
    created_at: datetime


class QuestionRequest(BaseModel):
    child_id: str
    subject: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)


class Question(BaseModel):
    id: str
    standard_ref: Optional[str] = None
    subject: str
    grade: Optional[int] = None
    topic: Optional[str] = None
    sub_topic: Optional[str] = None
    difficulty: Optional[str] = None
    stem: str
    options: list[str]
    correct_answer: str
    rationale: Optional[str] = None
    source: Optional[str] = None
    hash: str


class QuestionResponse(BaseModel):
    questions: list[Question]
    selected_subtopic: Optional[str] = None
    session_id: Optional[str] = None


class AttemptSubmission(BaseModel):
    child_id: str
    question_id: str
    selected: str
    time_spent_ms: int = Field(ge=0)


class AttemptResult(BaseModel):
    attempt_id: str
    correct: bool
    expected: str


class SubjectBreakdown(BaseModel):
    correct: int
    total: int
    accuracy: int  # Percentage 0-100


class ProgressResponse(BaseModel):
    attempted: int
    correct: int
    accuracy: int  # Percentage 0-100
    current_streak: int
    by_subject: dict[str, SubjectBreakdown]


class Session(BaseModel):
    """Practice session tracking."""
    id: str
    child_id: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SessionSummary(BaseModel):
    """Summary statistics for a practice session."""
    session: Session
    questions_attempted: int
    questions_correct: int
    accuracy: int  # Percentage 0-100
    total_time_ms: int
    avg_time_per_question_ms: int
    subjects_practiced: list[str]


class Standard(BaseModel):
    subject: str
    grade: int
    domain: Optional[str]
    sub_domain: Optional[str]
    standard_ref: str
    title: Optional[str]
    description: Optional[str]


class AdminGenerateRequest(BaseModel):
    subject: str
    topic: Optional[str] = None
    grade: Optional[int] = None
    difficulty: Optional[str] = Field(default="medium")
    count: int = Field(default=5, ge=1, le=20)


# Quiz Mode Models

class DifficultyMix(BaseModel):
    """Difficulty mix configuration for quiz."""
    easy: float = Field(default=0.3, ge=0, le=1)
    medium: float = Field(default=0.5, ge=0, le=1)
    hard: float = Field(default=0.2, ge=0, le=1)

    @field_validator("hard")
    @classmethod
    def _validate_sum(cls, value: float, info) -> float:
        """Ensure difficulty proportions sum to 1.0."""
        if hasattr(info, 'data'):
            easy = info.data.get('easy', 0.3)
            medium = info.data.get('medium', 0.5)
            total = easy + medium + value
            if not (0.99 <= total <= 1.01):  # Allow small floating point error
                raise ValueError("Difficulty mix proportions must sum to 1.0")
        return value


class QuizCreateRequest(BaseModel):
    """Request to create a new quiz session."""
    child_id: str
    subject: str
    topic: str
    subtopic: Optional[str] = None
    question_count: int = Field(ge=5, le=30)
    duration_sec: int = Field(ge=300, le=7200)  # 5 min to 2 hours
    difficulty_mix: Optional[DifficultyMix] = None


class QuizSessionQuestion(BaseModel):
    """A question within a quiz session."""
    id: str
    quiz_session_id: str
    question_id: str
    index: int  # Order in the quiz
    correct_choice: str
    explanation: str
    selected_choice: Optional[str] = None
    is_correct: Optional[bool] = None


class QuizSession(BaseModel):
    """A quiz session."""
    id: str
    child_id: str
    subject: str
    topic: str
    subtopic: Optional[str] = None
    status: str  # active, completed, expired
    duration_sec: int
    difficulty_mix_config: dict
    started_at: datetime
    submitted_at: Optional[datetime] = None
    score: Optional[int] = None  # Percentage 0-100
    total_questions: int
    created_at: datetime


class QuizQuestionDisplay(BaseModel):
    """Question displayed to user during quiz (no answers/explanations)."""
    id: str
    index: int
    stem: str
    options: list[str]
    difficulty: Optional[str] = None
    subject: str
    topic: Optional[str] = None


class QuizSessionResponse(BaseModel):
    """Response when creating or fetching a quiz session."""
    session: QuizSession
    questions: list[QuizQuestionDisplay]
    time_remaining_sec: Optional[int] = None


class QuizAnswerSubmission(BaseModel):
    """Answer submission for a single question."""
    question_id: str
    selected_choice: str


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers."""
    answers: list[QuizAnswerSubmission]


class QuizIncorrectItem(BaseModel):
    """Details for an incorrect answer."""
    question_id: str
    index: int
    stem: str
    options: list[str]
    selected_choice: str
    correct_choice: str
    explanation: str


class QuizResult(BaseModel):
    """Results after quiz submission."""
    session_id: str
    score: int  # Percentage 0-100
    correct_count: int
    total_questions: int
    time_taken_sec: int
    incorrect_items: list[QuizIncorrectItem]
    submitted_at: datetime


class QuizFeedback(BaseModel):
    """User feedback for quiz experience."""
    duration_appropriate: Literal['too_short', 'just_right', 'too_long']
    questions_fair: Literal['too_easy', 'appropriate', 'too_hard']
    overall_rating: Literal[1, 2, 3, 4, 5]
    comments: Optional[str] = None
