"""Pydantic schemas for request/response bodies."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

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
