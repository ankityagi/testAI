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
    selected_subtopic: str | None = None


def _difficulty_sequence(attempts: Sequence[dict]) -> list[str]:
    if not attempts:
        return ["easy", "medium"]
    correct = sum(1 for attempt in attempts if attempt.get("correct"))
    accuracy = correct / len(attempts)
    if accuracy >= 0.95 and len(attempts) >= 10:
        return ["medium", "hard", "easy"]
    if accuracy >= 0.8:
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


def select_next_subtopic(
    *,
    repo,
    child_id: str,
    subject: str,
    topic: str,
    grade: int,
) -> str | None:
    """
    Select the next subtopic for a child to work on.
    Prioritizes subtopics with more unseen questions, then by sequence order.

    Returns None if no subtopics exist for the topic.
    """
    # Get all subtopics for this topic
    subtopics = repo.list_subtopics(subject=subject, grade=grade, topic=topic)

    if not subtopics:
        print(f"[SELECT_SUBTOPIC] No subtopics found for {subject}/{grade}/{topic}", flush=True)
        return None

    # For each subtopic, count unseen questions
    subtopic_scores = []
    seen_hashes = set(repo.list_seen_question_hashes(child_id))

    for st in subtopics:
        subtopic_name = st["subtopic"]

        # Get all questions for this subtopic
        all_questions = repo.list_questions(
            subject=subject,
            grade=grade,
            topic=topic,
            subtopic=subtopic_name
        )

        # Count unseen
        unseen = sum(1 for q in all_questions if q["hash"] not in seen_hashes)

        subtopic_scores.append({
            "subtopic": subtopic_name,
            "unseen": unseen,
            "sequence_order": st.get("sequence_order", 999)
        })

    # Sort by unseen (DESC), then sequence_order (ASC)
    subtopic_scores.sort(key=lambda x: (-x["unseen"], x["sequence_order"]))

    selected = subtopic_scores[0]["subtopic"]
    print(f"[SELECT_SUBTOPIC] Selected: {selected} (unseen: {subtopic_scores[0]['unseen']})", flush=True)

    return selected


def fetch_batch(
    *,
    repo,
    child: dict,
    subject: str,
    topic: str | None,
    subtopic: str | None = None,
    limit: int,
    generator=generate_mcqs,
) -> QuestionBatch:
    child_id = child["id"]
    grade = child.get("grade")

    # AUTO-SELECT subtopic if not provided
    if subtopic is None and topic:
        subtopic = select_next_subtopic(
            repo=repo,
            child_id=child_id,
            subject=subject,
            topic=topic,
            grade=grade
        )
        print(f"[FETCH_BATCH] Auto-selected subtopic: {subtopic}", flush=True)
    else:
        print(f"[FETCH_BATCH] Using provided subtopic: {subtopic}", flush=True)

    attempts = repo.list_child_attempts(child_id)
    difficulty_preferences = _difficulty_sequence(attempts)
    seen_hashes = set(repo.list_seen_question_hashes(child_id))

    available_questions: list[dict] = []
    for difficulty in difficulty_preferences:
        fetched = repo.list_questions(
            subject=subject,
            topic=topic,
            grade=grade,
            subtopic=subtopic,
            difficulties=[difficulty],
            exclude_hashes=seen_hashes,
        )
        print(f"[PICKER] Fetched {len(fetched)} questions from DB for subject={subject}, topic={topic}, subtopic={subtopic}, grade={grade}, difficulty={difficulty}", flush=True)
        for question in fetched:
            question.setdefault("difficulty", difficulty)
            print(f"[PICKER] Question source: {question.get('source', 'unknown')}, stem: {question.get('stem', '')[:80]}", flush=True)
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
    print(f"[PICKER] Picked {len(picked)} from DB, need {limit}, deficit={deficit}", flush=True)
    if deficit > 0:
        print(f"[PICKER] Generating {deficit} questions via AI for immediate use", flush=True)
        preferred_difficulty = difficulty_preferences[0]
        ctx = GenerationContext(
            subject=subject,
            topic=topic,
            grade=grade,
            subtopic=subtopic,  # Include subtopic in generation
            difficulty=preferred_difficulty,
            count=deficit,
        )
        generated = [
            _normalise_question(item, subject=subject, topic=topic, grade=grade, difficulty=preferred_difficulty)
            for item in generator(context=ctx)
        ]
        # Ensure generated questions have the correct subtopic
        for q in generated:
            q.setdefault("sub_topic", subtopic)

        generated = _unique_questions(generated, seen_for_session)
        print(f"[PICKER] Generated {len(generated)} unique questions for subtopic: {subtopic}", flush=True)
        if generated:
            repo.insert_questions(generated)
            for q in generated[:deficit]:
                print(f"[PICKER] Adding generated question with id: {q.get('id')}", flush=True)
            picked.extend(generated[:deficit])

    # Check stock level for THIS SPECIFIC subtopic
    # After serving this request, calculate what we'll have left
    stock_level = repo.count_questions(
        subject=subject,
        topic=topic,
        grade=grade,
        subtopic=subtopic
    )

    # Calculate buffer needed to maintain MIN_STOCK_THRESHOLD
    # We want to ensure we always have at least 10 questions available
    questions_being_served = len(picked)
    remaining_after_request = stock_level - questions_being_served
    stock_deficit = max(MIN_STOCK_THRESHOLD - remaining_after_request, 0)

    if stock_deficit > 0:
        print(f"[FETCH_BATCH] Stock level after request: {remaining_after_request}, "
              f"triggering background generation of {stock_deficit} questions", flush=True)
    else:
        print(f"[FETCH_BATCH] Stock level after request: {remaining_after_request}, buffer maintained", flush=True)

    return QuestionBatch(
        questions=picked[:limit],
        stock_deficit=stock_deficit,
        selected_subtopic=subtopic
    )


def top_up_stock(
    *,
    repo,
    child: dict,
    subject: str,
    topic: str | None,
    subtopic: str | None = None,
    count: int,
    generator=generate_mcqs,
) -> None:
    """Generate questions to restock inventory for a SPECIFIC subtopic."""
    print(f"[TOP_UP] Generating {count} questions for {subject}/{topic}/{subtopic}", flush=True)

    grade = child.get("grade")
    ctx = GenerationContext(
        subject=subject,
        topic=topic,
        grade=grade,
        subtopic=subtopic,
        difficulty="medium",
        count=count,
    )
    generated = generator(context=ctx)
    normalised = [
        _normalise_question(item, subject=subject, topic=topic, grade=grade, difficulty=item.get("difficulty", "medium"))
        for item in generated
    ]
    repo.insert_questions(normalised)
    print(f"[TOP_UP] Successfully generated and inserted {len(normalised)} questions", flush=True)


__all__ = ["fetch_batch", "top_up_stock", "QuestionBatch"]
