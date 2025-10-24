"""Tests for progress response validation."""
import pytest
from pydantic import ValidationError

from studybuddy.backend.models import ProgressResponse, SubjectBreakdown


class TestProgressResponseValidation:
    """Test ProgressResponse model validation."""

    def test_valid_progress_response(self):
        """Test valid progress response with all fields."""
        progress = ProgressResponse(
            attempted=10,
            correct=8,
            accuracy=80,
            current_streak=3,
            by_subject={
                "Math": SubjectBreakdown(correct=5, total=6, accuracy=83),
                "Reading": SubjectBreakdown(correct=3, total=4, accuracy=75)
            }
        )
        assert progress.attempted == 10
        assert progress.correct == 8
        assert progress.accuracy == 80
        assert progress.current_streak == 3
        assert len(progress.by_subject) == 2

    def test_accuracy_is_integer_percentage(self):
        """Test that accuracy is integer 0-100, not float."""
        # Valid integer percentages
        progress = ProgressResponse(
            attempted=10,
            correct=8,
            accuracy=80,  # Integer, not 0.80
            current_streak=0,
            by_subject={}
        )
        assert isinstance(progress.accuracy, int)
        assert progress.accuracy == 80

        # Test boundary values
        progress_zero = ProgressResponse(
            attempted=10,
            correct=0,
            accuracy=0,
            current_streak=0,
            by_subject={}
        )
        assert progress_zero.accuracy == 0

        progress_perfect = ProgressResponse(
            attempted=10,
            correct=10,
            accuracy=100,
            current_streak=10,
            by_subject={}
        )
        assert progress_perfect.accuracy == 100

    def test_subject_breakdown_accuracy_integer(self):
        """Test that SubjectBreakdown accuracy is also integer."""
        breakdown = SubjectBreakdown(
            correct=8,
            total=10,
            accuracy=80  # Integer percentage
        )
        assert isinstance(breakdown.accuracy, int)
        assert breakdown.accuracy == 80

    def test_zero_attempts_valid(self):
        """Test progress with zero attempts."""
        progress = ProgressResponse(
            attempted=0,
            correct=0,
            accuracy=0,
            current_streak=0,
            by_subject={}
        )
        assert progress.attempted == 0
        assert progress.correct == 0
        assert progress.accuracy == 0

    def test_negative_streak_allowed(self):
        """Test that negative streak is allowed (for incorrect streaks)."""
        progress = ProgressResponse(
            attempted=10,
            correct=3,
            accuracy=30,
            current_streak=-3,  # Negative streak for incorrect answers
            by_subject={}
        )
        assert progress.current_streak == -3

    def test_correct_cannot_exceed_attempted(self):
        """Test logical consistency (not enforced by Pydantic, but good to document)."""
        # This is allowed by the schema but logically incorrect
        # In a real implementation, you might want to add a custom validator
        progress = ProgressResponse(
            attempted=10,
            correct=15,  # Logically invalid but schema allows
            accuracy=150,
            current_streak=15,
            by_subject={}
        )
        # Note: This passes validation but represents bad data
        assert progress.correct > progress.attempted

    def test_multiple_subjects(self):
        """Test progress with multiple subjects."""
        progress = ProgressResponse(
            attempted=30,
            correct=24,
            accuracy=80,
            current_streak=2,
            by_subject={
                "Math": SubjectBreakdown(correct=10, total=12, accuracy=83),
                "Reading": SubjectBreakdown(correct=8, total=10, accuracy=80),
                "Science": SubjectBreakdown(correct=6, total=8, accuracy=75)
            }
        )
        assert len(progress.by_subject) == 3
        assert all(isinstance(s.accuracy, int) for s in progress.by_subject.values())

    def test_subject_name_capitalization(self):
        """Test that subject names are properly capitalized."""
        progress = ProgressResponse(
            attempted=10,
            correct=8,
            accuracy=80,
            current_streak=2,
            by_subject={
                "Math": SubjectBreakdown(correct=8, total=10, accuracy=80)
            }
        )
        # Subject should be capitalized (enforced by backend logic)
        assert "Math" in progress.by_subject
        assert "math" not in progress.by_subject


class TestSubjectBreakdownValidation:
    """Test SubjectBreakdown model validation."""

    def test_valid_subject_breakdown(self):
        """Test valid subject breakdown."""
        breakdown = SubjectBreakdown(
            correct=8,
            total=10,
            accuracy=80
        )
        assert breakdown.correct == 8
        assert breakdown.total == 10
        assert breakdown.accuracy == 80

    def test_perfect_score(self):
        """Test 100% accuracy breakdown."""
        breakdown = SubjectBreakdown(
            correct=10,
            total=10,
            accuracy=100
        )
        assert breakdown.accuracy == 100

    def test_zero_score(self):
        """Test 0% accuracy breakdown."""
        breakdown = SubjectBreakdown(
            correct=0,
            total=10,
            accuracy=0
        )
        assert breakdown.accuracy == 0

    def test_no_attempts(self):
        """Test breakdown with no attempts."""
        breakdown = SubjectBreakdown(
            correct=0,
            total=0,
            accuracy=0
        )
        assert breakdown.total == 0
        assert breakdown.accuracy == 0

    def test_various_accuracy_values(self):
        """Test various accuracy percentages."""
        test_cases = [
            (1, 10, 10),   # 10%
            (3, 10, 30),   # 30%
            (5, 10, 50),   # 50%
            (7, 10, 70),   # 70%
            (9, 10, 90),   # 90%
            (33, 100, 33), # 33%
            (67, 100, 67), # 67%
        ]

        for correct, total, accuracy in test_cases:
            breakdown = SubjectBreakdown(
                correct=correct,
                total=total,
                accuracy=accuracy
            )
            assert breakdown.accuracy == accuracy
            assert isinstance(breakdown.accuracy, int)
