"""Quiz grading service."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QuizGradingResult:
    """Result of quiz grading."""
    score: int  # Percentage 0-100
    correct_count: int
    total_questions: int
    unanswered_count: int
    incorrect_items: list[dict]
    time_taken_sec: int


def grade_quiz(
    *,
    session: dict,
    questions: list[dict],
    answers: list[dict],
) -> QuizGradingResult:
    """
    Grade a quiz session.

    Args:
        session: Quiz session dict with started_at timestamp
        questions: List of quiz questions with correct_choice and explanation
        answers: List of submitted answers with question_id and selected_choice

    Returns:
        QuizGradingResult with score and incorrect items
    """
    session_id = session["id"]
    started_at = session["started_at"]

    logger.info(f"[QUIZ] Grading quiz session {session_id}")

    # Create answer lookup
    answer_map = {ans["question_id"]: ans["selected_choice"] for ans in answers}

    # Grade each question
    correct_count = 0
    unanswered_count = 0
    incorrect_items = []

    for question in questions:
        question_id = question["question_id"]
        correct_choice = question["correct_choice"]
        selected_choice = answer_map.get(question_id)

        # Check if unanswered
        if selected_choice is None:
            unanswered_count += 1
            # Treat unanswered as incorrect
            incorrect_items.append({
                "question_id": question_id,
                "index": question["index"],
                "stem": question["stem"],
                "options": question["options"],
                "selected_choice": "",  # Empty for unanswered
                "correct_choice": correct_choice,
                "explanation": question["explanation"]
            })
            continue

        # Check if correct
        is_correct = (selected_choice == correct_choice)

        if is_correct:
            correct_count += 1
        else:
            incorrect_items.append({
                "question_id": question_id,
                "index": question["index"],
                "stem": question["stem"],
                "options": question["options"],
                "selected_choice": selected_choice,
                "correct_choice": correct_choice,
                "explanation": question["explanation"]
            })

    total_questions = len(questions)
    score = round((correct_count / total_questions * 100)) if total_questions else 0

    # Calculate time taken
    now = datetime.utcnow()
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
    time_taken_sec = int((now - started_at).total_seconds())

    logger.info(
        f"[QUIZ] Grading complete: {correct_count}/{total_questions} correct "
        f"({score}%), {unanswered_count} unanswered, took {time_taken_sec}s"
    )

    return QuizGradingResult(
        score=score,
        correct_count=correct_count,
        total_questions=total_questions,
        unanswered_count=unanswered_count,
        incorrect_items=incorrect_items,
        time_taken_sec=time_taken_sec
    )
