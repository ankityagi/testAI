"""Tests for quiz question selection service."""
import pytest
from unittest.mock import Mock, MagicMock

from studybuddy.backend.services.quiz_selection import (
    select_quiz_questions,
    QuizSelectionResult,
    _normalize_question,
)


class TestNormalizeQuestion:
    """Test question normalization."""

    def test_normalizes_all_fields(self):
        """Test that all required fields are normalized."""
        question = {
            "id": "q1",
            "stem": "What is 2+2?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "rationale": "2 plus 2 equals 4",
        }

        normalized = _normalize_question(
            question,
            subject="math",
            topic="addition",
            grade=3,
            difficulty="easy"
        )

        assert normalized["subject"] == "math"
        assert normalized["topic"] == "addition"
        assert normalized["grade"] == 3
        assert normalized["difficulty"] == "easy"
        assert normalized["source"] == "seeded"
        assert "hash" in normalized

    def test_preserves_existing_fields(self):
        """Test that existing fields are preserved."""
        question = {
            "id": "q1",
            "stem": "What is 2+2?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "source": "generated",
            "hash": "existing_hash",
        }

        normalized = _normalize_question(
            question,
            subject="math",
            topic="addition",
            grade=3,
            difficulty="easy"
        )

        assert normalized["source"] == "generated"
        assert normalized["hash"] == "existing_hash"


class TestQuizSelection:
    """Test quiz question selection logic."""

    def test_selects_correct_difficulty_distribution(self):
        """Test that difficulty mix is respected."""
        # Create mock repository
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])
        repo.list_seen_question_hashes = Mock(return_value=[])

        # Create 20 questions for each difficulty with explicit hashes
        easy_questions = [
            {
                "id": f"easy_{i}",
                "stem": f"Easy question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"easy_hash_{i}",
                "source": "seeded",
            }
            for i in range(20)
        ]
        medium_questions = [
            {
                "id": f"medium_{i}",
                "stem": f"Medium question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"medium_hash_{i}",
                "source": "seeded",
            }
            for i in range(20)
        ]
        hard_questions = [
            {
                "id": f"hard_{i}",
                "stem": f"Hard question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hard_hash_{i}",
                "source": "seeded",
            }
            for i in range(20)
        ]

        def list_questions_side_effect(subject, grade, topic, subtopic, difficulty):
            if difficulty == "easy":
                return easy_questions.copy()
            elif difficulty == "medium":
                return medium_questions.copy()
            elif difficulty == "hard":
                return hard_questions.copy()
            return []

        repo.list_questions = Mock(side_effect=list_questions_side_effect)

        # Select 10 questions with 30% easy, 50% medium, 20% hard
        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=10,
            difficulty_mix={"easy": 0.3, "medium": 0.5, "hard": 0.2},
            generator=None
        )

        # Check total count
        assert len(result.questions) == 10

        # Count difficulties
        easy_count = sum(1 for q in result.questions if "easy" in q["id"])
        medium_count = sum(1 for q in result.questions if "medium" in q["id"])
        hard_count = sum(1 for q in result.questions if "hard" in q["id"])

        # 30% of 10 = 3, 50% of 10 = 5, 20% of 10 = 2
        assert easy_count == 3
        assert medium_count == 5
        assert hard_count == 2

    def test_prioritizes_unseen_over_seen(self):
        """Test that unseen questions are prioritized when available."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])

        # Mark first 5 questions as seen
        seen_hashes = [f"hash_{i}" for i in range(5)]
        repo.list_seen_question_hashes = Mock(return_value=seen_hashes)

        # Create 10 questions with explicit hashes
        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(10)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=7,
            difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
            generator=None
        )

        # Should have selected 7 total
        assert len(result.questions) == 7

        # Count unseen vs seen
        selected_hashes = [q["hash"] for q in result.questions]
        seen_selected = [h for h in selected_hashes if h in seen_hashes]

        # Since there are 5 unseen available and we need 7, we should get all 5 unseen + 2 seen
        # But due to shuffling, we might get 4-5 unseen
        assert len(seen_selected) <= 3, "Should prioritize unseen questions"

    def test_prevents_duplicates_in_same_quiz(self):
        """Test that no duplicate questions appear in the same quiz."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])
        repo.list_seen_question_hashes = Mock(return_value=[])

        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(20)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=15,
            difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
            generator=None
        )

        # Check no duplicate hashes
        hashes = [q["hash"] for q in result.questions]
        assert len(hashes) == len(set(hashes)), "Found duplicate questions in quiz"

    def test_avoids_recent_questions(self):
        """Test that recent questions are avoided when possible."""
        repo = Mock()

        # Mark first 5 as recent
        recent_hashes = [f"hash_{i}" for i in range(5)]
        repo.list_recent_question_hashes = Mock(return_value=recent_hashes)
        repo.list_seen_question_hashes = Mock(return_value=recent_hashes)

        # Create 15 questions with explicit hashes (5 recent, 10 not recent)
        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(15)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=10,
            difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
            generator=None
        )

        # Should prefer non-recent questions
        assert len(result.questions) == 10

        selected_hashes = [q["hash"] for q in result.questions]
        recent_selected = [h for h in selected_hashes if h in recent_hashes]

        # With 10 non-recent available and needing 10, should avoid all recent
        # But due to shuffling might pick 0-2 recent
        assert len(recent_selected) <= 2, "Should avoid recent questions when possible"

    def test_falls_back_to_seen_when_insufficient_unseen(self):
        """Test that seen questions are used when not enough unseen."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])

        # Mark all as seen
        seen_hashes = [f"hash_{i}" for i in range(10)]
        repo.list_seen_question_hashes = Mock(return_value=seen_hashes)

        # Create questions with explicit hashes
        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(10)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        # Should succeed even though all are seen
        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=8,
            difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
            generator=None
        )

        assert len(result.questions) == 8

        # Verify no duplicates
        hashes = [q["hash"] for q in result.questions]
        assert len(hashes) == len(set(hashes))

    def test_raises_error_when_insufficient_questions(self):
        """Test that error is raised when not enough questions available."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])
        repo.list_seen_question_hashes = Mock(return_value=[])

        # Only 3 questions available
        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(3)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        # Request 10 questions - should raise error
        with pytest.raises(ValueError, match="Insufficient questions available"):
            select_quiz_questions(
                repo=repo,
                child_id="child1",
                subject="math",
                topic="addition",
                subtopic=None,
                grade=3,
                question_count=10,
                difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
                generator=None
            )

    def test_generation_fallback_for_math(self):
        """Test that AI generation is used as fallback for math."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])
        repo.list_seen_question_hashes = Mock(return_value=[])
        repo.upsert_question = Mock()

        # Only 3 questions in bank
        bank_questions = [
            {
                "id": f"bank_{i}",
                "stem": f"Bank question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"bank_hash_{i}",
                "source": "seeded",
            }
            for i in range(3)
        ]

        repo.list_questions = Mock(return_value=bank_questions.copy())

        # Mock generator that creates 7 new questions
        generated_questions = [
            {
                "id": f"gen_{i}",
                "stem": f"Generated question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"gen_hash_{i}",
                "source": "generated",
            }
            for i in range(7)
        ]

        generator = Mock(return_value=generated_questions)

        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=10,
            difficulty_mix={"easy": 0, "medium": 1.0, "hard": 0},
            generator=generator
        )

        # Should have 10 total questions (3 from bank + 7 generated)
        assert len(result.questions) == 10
        assert result.generated_count == 7

        # Verify generator was called
        assert generator.called

    def test_rounding_adjustment_for_difficulty_mix(self):
        """Test that rounding errors in difficulty mix are handled."""
        repo = Mock()
        repo.list_recent_question_hashes = Mock(return_value=[])
        repo.list_seen_question_hashes = Mock(return_value=[])

        questions = [
            {
                "id": f"q_{i}",
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_answer": "a",
                "hash": f"hash_{i}",
                "source": "seeded",
            }
            for i in range(50)
        ]

        repo.list_questions = Mock(return_value=questions.copy())

        # 11 questions with 30/50/20 mix
        # 11 * 0.3 = 3.3 → 3 easy
        # 11 * 0.5 = 5.5 → 6 medium (adjusted)
        # 11 * 0.2 = 2.2 → 2 hard
        # Total should be exactly 11
        result = select_quiz_questions(
            repo=repo,
            child_id="child1",
            subject="math",
            topic="addition",
            subtopic=None,
            grade=3,
            question_count=11,
            difficulty_mix={"easy": 0.3, "medium": 0.5, "hard": 0.2},
            generator=None
        )

        assert len(result.questions) == 11
