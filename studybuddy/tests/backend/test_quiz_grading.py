"""Tests for quiz grading service."""
import pytest
from datetime import datetime, timedelta

from studybuddy.backend.services.quiz_grading import (
    grade_quiz,
    QuizGradingResult,
)


class TestQuizGrading:
    """Test quiz grading logic."""

    def test_perfect_score(self):
        """Test all correct answers yields 100%."""
        session = {
            "id": "session1",
            "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "What is 2+2?",
                "options": ["2", "3", "4", "5"],
                "correct_choice": "4",
                "explanation": "2 plus 2 equals 4"
            },
            {
                "question_id": "q2",
                "index": 1,
                "stem": "What is 3+3?",
                "options": ["4", "5", "6", "7"],
                "correct_choice": "6",
                "explanation": "3 plus 3 equals 6"
            },
            {
                "question_id": "q3",
                "index": 2,
                "stem": "What is 5+5?",
                "options": ["8", "9", "10", "11"],
                "correct_choice": "10",
                "explanation": "5 plus 5 equals 10"
            }
        ]

        answers = [
            {"question_id": "q1", "selected_choice": "4"},
            {"question_id": "q2", "selected_choice": "6"},
            {"question_id": "q3", "selected_choice": "10"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert result.score == 100
        assert result.correct_count == 3
        assert result.total_questions == 3
        assert result.unanswered_count == 0
        assert len(result.incorrect_items) == 0

    def test_all_incorrect(self):
        """Test all incorrect answers yields 0%."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "What is 2+2?",
                "options": ["2", "3", "4", "5"],
                "correct_choice": "4",
                "explanation": "2 plus 2 equals 4"
            },
            {
                "question_id": "q2",
                "index": 1,
                "stem": "What is 3+3?",
                "options": ["4", "5", "6", "7"],
                "correct_choice": "6",
                "explanation": "3 plus 3 equals 6"
            }
        ]

        answers = [
            {"question_id": "q1", "selected_choice": "2"},
            {"question_id": "q2", "selected_choice": "5"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert result.score == 0
        assert result.correct_count == 0
        assert result.total_questions == 2
        assert result.unanswered_count == 0
        assert len(result.incorrect_items) == 2

    def test_mixed_results(self):
        """Test mixed correct/incorrect answers."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Question 1",
                "options": ["a", "b", "c", "d"],
                "correct_choice": "a",
                "explanation": "Explanation 1"
            },
            {
                "question_id": "q2",
                "index": 1,
                "stem": "Question 2",
                "options": ["a", "b", "c", "d"],
                "correct_choice": "b",
                "explanation": "Explanation 2"
            },
            {
                "question_id": "q3",
                "index": 2,
                "stem": "Question 3",
                "options": ["a", "b", "c", "d"],
                "correct_choice": "c",
                "explanation": "Explanation 3"
            },
            {
                "question_id": "q4",
                "index": 3,
                "stem": "Question 4",
                "options": ["a", "b", "c", "d"],
                "correct_choice": "d",
                "explanation": "Explanation 4"
            }
        ]

        # 3 correct, 1 incorrect = 75%
        answers = [
            {"question_id": "q1", "selected_choice": "a"},  # Correct
            {"question_id": "q2", "selected_choice": "b"},  # Correct
            {"question_id": "q3", "selected_choice": "c"},  # Correct
            {"question_id": "q4", "selected_choice": "a"}   # Incorrect
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert result.score == 75
        assert result.correct_count == 3
        assert result.total_questions == 4
        assert result.unanswered_count == 0
        assert len(result.incorrect_items) == 1
        assert result.incorrect_items[0]["question_id"] == "q4"

    def test_unanswered_questions(self):
        """Test that unanswered questions are counted as incorrect."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Question 1",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": "Explanation 1"
            },
            {
                "question_id": "q2",
                "index": 1,
                "stem": "Question 2",
                "options": ["a", "b"],
                "correct_choice": "b",
                "explanation": "Explanation 2"
            },
            {
                "question_id": "q3",
                "index": 2,
                "stem": "Question 3",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": "Explanation 3"
            }
        ]

        # Only answer q1 correctly, leave q2 and q3 unanswered
        answers = [
            {"question_id": "q1", "selected_choice": "a"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        # 1/3 correct = 33%
        assert result.score == 33
        assert result.correct_count == 1
        assert result.total_questions == 3
        assert result.unanswered_count == 2
        assert len(result.incorrect_items) == 2

        # Check unanswered items have empty selected_choice
        unanswered = [item for item in result.incorrect_items if item["selected_choice"] == ""]
        assert len(unanswered) == 2

    def test_incorrect_items_structure(self):
        """Test that incorrect items have all required fields."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Test question",
                "options": ["option1", "option2", "option3"],
                "correct_choice": "option1",
                "explanation": "Test explanation"
            }
        ]

        # Submit wrong answer
        answers = [
            {"question_id": "q1", "selected_choice": "option2"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert len(result.incorrect_items) == 1
        item = result.incorrect_items[0]

        # Verify all required fields
        assert item["question_id"] == "q1"
        assert item["index"] == 0
        assert item["stem"] == "Test question"
        assert item["options"] == ["option1", "option2", "option3"]
        assert item["selected_choice"] == "option2"
        assert item["correct_choice"] == "option1"
        assert item["explanation"] == "Test explanation"

    def test_score_rounding(self):
        """Test that scores are rounded correctly."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        # 2 correct out of 3 = 66.666...%
        questions = [
            {
                "question_id": f"q{i}",
                "index": i,
                "stem": f"Question {i}",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": f"Explanation {i}"
            }
            for i in range(3)
        ]

        answers = [
            {"question_id": "q0", "selected_choice": "a"},  # Correct
            {"question_id": "q1", "selected_choice": "a"},  # Correct
            {"question_id": "q2", "selected_choice": "b"}   # Incorrect
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        # 66.666... should round to 67
        assert result.score == 67
        assert result.correct_count == 2
        assert result.total_questions == 3

    def test_time_calculation(self):
        """Test that time taken is calculated correctly."""
        # Start 5 minutes ago
        started_at = datetime.utcnow() - timedelta(minutes=5)
        session = {
            "id": "session1",
            "started_at": started_at.isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Question",
                "options": ["a"],
                "correct_choice": "a",
                "explanation": "Explanation"
            }
        ]

        answers = [
            {"question_id": "q1", "selected_choice": "a"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        # Should be approximately 300 seconds (5 minutes)
        # Allow some tolerance for test execution time
        assert 295 <= result.time_taken_sec <= 305

    def test_single_question_quiz(self):
        """Test grading a quiz with only one question."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Only question",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": "Explanation"
            }
        ]

        # Correct answer
        answers = [
            {"question_id": "q1", "selected_choice": "a"}
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert result.score == 100
        assert result.correct_count == 1
        assert result.total_questions == 1
        assert len(result.incorrect_items) == 0

    def test_empty_answers_all_unanswered(self):
        """Test quiz submission with no answers provided."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": f"q{i}",
                "index": i,
                "stem": f"Question {i}",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": f"Explanation {i}"
            }
            for i in range(5)
        ]

        # Empty answers list
        answers = []

        result = grade_quiz(session=session, questions=questions, answers=answers)

        assert result.score == 0
        assert result.correct_count == 0
        assert result.total_questions == 5
        assert result.unanswered_count == 5
        assert len(result.incorrect_items) == 5

    def test_large_quiz_grading(self):
        """Test grading a large quiz (20 questions)."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": f"q{i}",
                "index": i,
                "stem": f"Question {i}",
                "options": ["a", "b", "c", "d"],
                "correct_choice": "a",
                "explanation": f"Explanation {i}"
            }
            for i in range(20)
        ]

        # Answer first 15 correctly, last 5 incorrectly
        answers = [
            {"question_id": f"q{i}", "selected_choice": "a"}
            for i in range(15)
        ] + [
            {"question_id": f"q{i}", "selected_choice": "b"}
            for i in range(15, 20)
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        # 15/20 = 75%
        assert result.score == 75
        assert result.correct_count == 15
        assert result.total_questions == 20
        assert result.unanswered_count == 0
        assert len(result.incorrect_items) == 5

    def test_datetime_object_parsing(self):
        """Test that both string and datetime objects work for started_at."""
        # Test with string ISO format
        session_str = {
            "id": "session1",
            "started_at": "2025-11-01T12:00:00Z"
        }

        # Test with datetime object
        session_dt = {
            "id": "session2",
            "started_at": datetime(2025, 11, 1, 12, 0, 0)
        }

        questions = [
            {
                "question_id": "q1",
                "index": 0,
                "stem": "Question",
                "options": ["a"],
                "correct_choice": "a",
                "explanation": "Explanation"
            }
        ]

        answers = [
            {"question_id": "q1", "selected_choice": "a"}
        ]

        # Both should work without errors
        result_str = grade_quiz(session=session_str, questions=questions, answers=answers)
        result_dt = grade_quiz(session=session_dt, questions=questions, answers=answers)

        assert result_str.score == 100
        assert result_dt.score == 100
        assert result_str.time_taken_sec > 0
        assert result_dt.time_taken_sec > 0

    def test_partial_answers(self):
        """Test quiz with some questions answered, some not."""
        session = {
            "id": "session1",
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        questions = [
            {
                "question_id": f"q{i}",
                "index": i,
                "stem": f"Question {i}",
                "options": ["a", "b"],
                "correct_choice": "a",
                "explanation": f"Explanation {i}"
            }
            for i in range(10)
        ]

        # Answer questions 0, 2, 4, 6, 8 correctly (odd indices unanswered)
        answers = [
            {"question_id": f"q{i}", "selected_choice": "a"}
            for i in range(0, 10, 2)
        ]

        result = grade_quiz(session=session, questions=questions, answers=answers)

        # 5/10 = 50%
        assert result.score == 50
        assert result.correct_count == 5
        assert result.total_questions == 10
        assert result.unanswered_count == 5
        assert len(result.incorrect_items) == 5
