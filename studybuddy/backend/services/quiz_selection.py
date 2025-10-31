"""Quiz question selection service with mixed difficulty sampling."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass

from .genai import GenerationContext, generate_mcqs
from .hashing import hash_question

logger = logging.getLogger(__name__)


@dataclass
class QuizSelectionResult:
    """Result of quiz question selection."""
    questions: list[dict]
    selected_subtopic: str | None = None
    generated_count: int = 0


def _normalize_question(question: dict, *, subject: str, topic: str, grade: int | None, difficulty: str) -> dict:
    """Normalize question fields."""
    question.setdefault("id", question.get("question_id"))
    question.setdefault("subject", subject)
    question.setdefault("topic", topic)
    question.setdefault("difficulty", difficulty)
    question.setdefault("grade", grade)
    question.setdefault("source", question.get("source", "seeded"))
    question.setdefault("options", question.get("options", []))
    question.setdefault("correct_answer", question.get("correct_answer"))
    question.setdefault("rationale", question.get("rationale", ""))
    options = question["options"]
    answer = question["correct_answer"]
    stem = question["stem"]
    question["hash"] = question.get("hash") or hash_question(stem, options, answer)
    return question


def select_quiz_questions(
    *,
    repo,
    child_id: str,
    subject: str,
    topic: str,
    subtopic: str | None,
    grade: int | None,
    question_count: int,
    difficulty_mix: dict,
    generator=generate_mcqs,
) -> QuizSelectionResult:
    """
    Select questions for a quiz with specified difficulty mix.

    Args:
        repo: Repository instance
        child_id: Child ID for tracking seen questions
        subject: Subject (e.g., "math", "reading")
        topic: Topic within subject
        subtopic: Subtopic (optional)
        grade: Grade level
        question_count: Total questions needed
        difficulty_mix: Dict with 'easy', 'medium', 'hard' proportions (sum to 1.0)
        generator: Question generator function (for fallback)

    Returns:
        QuizSelectionResult with selected questions
    """
    logger.info(
        f"[QUIZ] Selecting {question_count} questions for {subject}/{topic}"
        f" (grade {grade}) with mix {difficulty_mix}"
    )

    # Calculate target count per difficulty
    target_counts = {
        "easy": round(question_count * difficulty_mix.get("easy", 0.3)),
        "medium": round(question_count * difficulty_mix.get("medium", 0.5)),
        "hard": round(question_count * difficulty_mix.get("hard", 0.2)),
    }

    # Adjust for rounding errors
    total_target = sum(target_counts.values())
    if total_target < question_count:
        # Add remaining to medium
        target_counts["medium"] += (question_count - total_target)
    elif total_target > question_count:
        # Remove excess from medium
        target_counts["medium"] -= (total_target - question_count)

    logger.info(f"[QUIZ] Target counts: easy={target_counts['easy']}, "
                f"medium={target_counts['medium']}, hard={target_counts['hard']}")

    # Get seen question hashes to prioritize unseen
    seen_hashes = set(repo.list_seen_question_hashes(child_id))
    logger.info(f"[QUIZ] Child has seen {len(seen_hashes)} questions previously")

    selected_questions = []
    question_hashes = set()  # Track hashes to prevent duplicates in this quiz
    generated_count = 0

    # Select questions for each difficulty level
    for difficulty in ["easy", "medium", "hard"]:
        target = target_counts[difficulty]
        if target == 0:
            continue

        logger.info(f"[QUIZ] Selecting {target} {difficulty} questions...")

        # Fetch all questions for this difficulty
        all_questions = repo.list_questions(
            subject=subject,
            grade=grade,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty
        )

        logger.info(f"[QUIZ] Found {len(all_questions)} {difficulty} questions in bank")

        # Normalize questions
        all_questions = [
            _normalize_question(q, subject=subject, topic=topic, grade=grade, difficulty=difficulty)
            for q in all_questions
        ]

        # Separate unseen vs seen
        unseen = [q for q in all_questions if q["hash"] not in seen_hashes and q["hash"] not in question_hashes]
        seen = [q for q in all_questions if q["hash"] in seen_hashes and q["hash"] not in question_hashes]

        logger.info(f"[QUIZ] {difficulty}: {len(unseen)} unseen, {len(seen)} seen (available)")

        # Prioritize unseen, fallback to seen
        available = unseen + seen

        # Shuffle to randomize order
        random.shuffle(available)

        # Select up to target
        selected = available[:target]

        # Track selected hashes
        for q in selected:
            question_hashes.add(q["hash"])

        selected_questions.extend(selected)

        # If we don't have enough, try to generate more
        deficit = target - len(selected)
        if deficit > 0:
            logger.warning(
                f"[QUIZ] Insufficient {difficulty} questions: needed {target}, found {len(selected)}, "
                f"deficit {deficit}"
            )

            # Try to generate if we have a generator and it's math (Eureka)
            if generator and subject.lower() == "math":
                logger.info(f"[QUIZ] Attempting to generate {deficit} {difficulty} math questions")

                try:
                    context = GenerationContext(
                        subject=subject,
                        topic=topic,
                        subtopic=subtopic,
                        grade=grade,
                        difficulty=difficulty,
                        count=deficit
                    )

                    generated = generator(context)
                    logger.info(f"[QUIZ] Generated {len(generated)} {difficulty} questions")

                    # Normalize and deduplicate
                    for q in generated:
                        q = _normalize_question(q, subject=subject, topic=topic, grade=grade, difficulty=difficulty)
                        if q["hash"] not in question_hashes and q["hash"] not in seen_hashes:
                            # Store in repo
                            repo.upsert_question(q)
                            selected_questions.append(q)
                            question_hashes.add(q["hash"])
                            generated_count += 1
                            if len(selected_questions) >= question_count:
                                break

                    logger.info(f"[QUIZ] Added {generated_count} unique generated questions")

                except Exception as e:
                    logger.error(f"[QUIZ] Generation failed for {difficulty}: {e}")

    # If we still don't have enough questions, raise error
    if len(selected_questions) < question_count:
        raise ValueError(
            f"Insufficient questions available: needed {question_count}, "
            f"only found {len(selected_questions)}"
        )

    # Verify no duplicates
    final_hashes = [q["hash"] for q in selected_questions]
    if len(final_hashes) != len(set(final_hashes)):
        logger.error("[QUIZ] Duplicate questions detected in quiz!")
        raise ValueError("Duplicate questions detected in selection")

    logger.info(
        f"[QUIZ] Selection complete: {len(selected_questions)} questions "
        f"(generated: {generated_count})"
    )

    return QuizSelectionResult(
        questions=selected_questions,
        selected_subtopic=subtopic,
        generated_count=generated_count
    )
