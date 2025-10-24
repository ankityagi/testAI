"""Tests for attempt submission validation and time tracking."""
import pytest
from pydantic import ValidationError

from studybuddy.backend.models import AttemptSubmission


class TestAttemptSubmissionValidation:
    """Test AttemptSubmission model validation."""

    def test_valid_attempt_submission(self):
        """Test valid attempt submission with all required fields."""
        attempt = AttemptSubmission(
            child_id="123e4567-e89b-12d3-a456-426614174000",
            question_id="123e4567-e89b-12d3-a456-426614174001",
            selected="Option A",
            time_spent_ms=5000
        )
        assert attempt.child_id == "123e4567-e89b-12d3-a456-426614174000"
        assert attempt.question_id == "123e4567-e89b-12d3-a456-426614174001"
        assert attempt.selected == "Option A"
        assert attempt.time_spent_ms == 5000

    def test_time_spent_ms_non_negative(self):
        """Test that time_spent_ms must be non-negative."""
        with pytest.raises(ValidationError) as exc_info:
            AttemptSubmission(
                child_id="123e4567-e89b-12d3-a456-426614174000",
                question_id="123e4567-e89b-12d3-a456-426614174001",
                selected="Option A",
                time_spent_ms=-100  # Invalid: negative
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("time_spent_ms",) and
            "greater than or equal to 0" in str(error["msg"]).lower()
            for error in errors
        )

    def test_time_spent_ms_zero_allowed(self):
        """Test that time_spent_ms can be zero."""
        attempt = AttemptSubmission(
            child_id="123e4567-e89b-12d3-a456-426614174000",
            question_id="123e4567-e89b-12d3-a456-426614174001",
            selected="Option A",
            time_spent_ms=0
        )
        assert attempt.time_spent_ms == 0

    def test_time_spent_ms_realistic_values(self):
        """Test realistic time_spent_ms values."""
        # Very quick answer (100ms)
        quick = AttemptSubmission(
            child_id="123e4567-e89b-12d3-a456-426614174000",
            question_id="123e4567-e89b-12d3-a456-426614174001",
            selected="Option A",
            time_spent_ms=100
        )
        assert quick.time_spent_ms == 100

        # Normal answer (30 seconds)
        normal = AttemptSubmission(
            child_id="123e4567-e89b-12d3-a456-426614174000",
            question_id="123e4567-e89b-12d3-a456-426614174001",
            selected="Option B",
            time_spent_ms=30000
        )
        assert normal.time_spent_ms == 30000

        # Slow answer (2 minutes)
        slow = AttemptSubmission(
            child_id="123e4567-e89b-12d3-a456-426614174000",
            question_id="123e4567-e89b-12d3-a456-426614174001",
            selected="Option C",
            time_spent_ms=120000
        )
        assert slow.time_spent_ms == 120000

    def test_missing_required_fields(self):
        """Test that all required fields must be provided."""
        with pytest.raises(ValidationError):
            AttemptSubmission(
                # Missing child_id
                question_id="123e4567-e89b-12d3-a456-426614174001",
                selected="Option A",
                time_spent_ms=5000
            )

        with pytest.raises(ValidationError):
            AttemptSubmission(
                child_id="123e4567-e89b-12d3-a456-426614174000",
                # Missing question_id
                selected="Option A",
                time_spent_ms=5000
            )

        with pytest.raises(ValidationError):
            AttemptSubmission(
                child_id="123e4567-e89b-12d3-a456-426614174000",
                question_id="123e4567-e89b-12d3-a456-426614174001",
                # Missing selected
                time_spent_ms=5000
            )

        with pytest.raises(ValidationError):
            AttemptSubmission(
                child_id="123e4567-e89b-12d3-a456-426614174000",
                question_id="123e4567-e89b-12d3-a456-426614174001",
                selected="Option A"
                # Missing time_spent_ms
            )
