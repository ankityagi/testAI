"""Validation helpers for generated questions."""
from __future__ import annotations

from typing import Any


class QuestionValidationError(ValueError):
    """Raised when a question payload fails validation."""


def validate_mcq(question: dict[str, Any]) -> None:
    options = question.get("options", [])
    if len(options) != 4:
        raise QuestionValidationError("Each question must carry exactly four options")
    answer = question.get("correct_answer")
    if answer not in options:
        raise QuestionValidationError("Correct answer must be one of the provided options")
    if len(set(options)) != 4:
        raise QuestionValidationError("Options must be unique")
