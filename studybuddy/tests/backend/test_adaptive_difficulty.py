"""Tests for adaptive difficulty algorithm."""
import pytest

from studybuddy.backend.services.question_picker import _difficulty_sequence


class TestAdaptiveDifficultySequence:
    """Test adaptive difficulty selection logic."""

    def test_no_attempts_returns_easy_medium(self):
        """Test that no previous attempts starts with easy/medium."""
        sequence = _difficulty_sequence([])
        assert sequence == ["easy", "medium"]

    def test_high_mastery_prioritizes_harder_questions(self):
        """Test ≥95% accuracy with ≥10 attempts prioritizes medium/hard."""
        # 10 attempts, 10 correct (100% accuracy)
        attempts = [{"correct": True} for _ in range(10)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["medium", "hard", "easy"]

        # 20 attempts, 19 correct (95% accuracy - threshold)
        attempts = [{"correct": True} for _ in range(19)] + [{"correct": False}]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["medium", "hard", "easy"]

    def test_high_mastery_requires_min_10_attempts(self):
        """Test that high mastery requires at least 10 attempts."""
        # 9 attempts, all correct (100% but < 10 attempts)
        attempts = [{"correct": True} for _ in range(9)]
        sequence = _difficulty_sequence(attempts)
        # Should use standard progression, not high mastery
        assert sequence == ["easy", "medium", "hard"]

    def test_strong_performance_standard_progression(self):
        """Test ≥80% accuracy uses standard easy → medium → hard."""
        # 10 attempts, 8 correct (80%)
        attempts = (
            [{"correct": True} for _ in range(8)] +
            [{"correct": False} for _ in range(2)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy", "medium", "hard"]

        # 15 attempts, 13 correct (86.7%)
        attempts = (
            [{"correct": True} for _ in range(13)] +
            [{"correct": False} for _ in range(2)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy", "medium", "hard"]

    def test_needs_practice_stays_easy(self):
        """Test <80% accuracy stays with easy questions."""
        # 10 attempts, 7 correct (70%)
        attempts = (
            [{"correct": True} for _ in range(7)] +
            [{"correct": False} for _ in range(3)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]

        # 10 attempts, 5 correct (50%)
        attempts = [{"correct": i < 5} for i in range(10)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]

    def test_exactly_80_percent_threshold(self):
        """Test that exactly 80% accuracy triggers progression."""
        # 10 attempts, exactly 8 correct (80%)
        attempts = (
            [{"correct": True} for _ in range(8)] +
            [{"correct": False} for _ in range(2)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy", "medium", "hard"]

    def test_exactly_95_percent_threshold(self):
        """Test that exactly 95% accuracy with 20 attempts triggers high mastery."""
        # 20 attempts, exactly 19 correct (95%)
        attempts = (
            [{"correct": True} for _ in range(19)] +
            [{"correct": False}]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["medium", "hard", "easy"]

    def test_just_below_thresholds(self):
        """Test performance just below thresholds."""
        # 79% (just below 80%)
        attempts = (
            [{"correct": True} for _ in range(79)] +
            [{"correct": False} for _ in range(21)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]

        # 94% with 10 attempts (just below 95%)
        attempts = (
            [{"correct": True} for _ in range(94)] +
            [{"correct": False} for _ in range(6)]
        )
        sequence = _difficulty_sequence(attempts)
        # Should use standard progression, not high mastery
        assert sequence == ["easy", "medium", "hard"]

    def test_single_attempt_scenarios(self):
        """Test behavior with only one attempt."""
        # One correct
        sequence = _difficulty_sequence([{"correct": True}])
        assert sequence == ["easy", "medium", "hard"]

        # One incorrect
        sequence = _difficulty_sequence([{"correct": False}])
        assert sequence == ["easy"]

    def test_many_attempts_scenarios(self):
        """Test behavior with many attempts."""
        # 100 attempts, 96 correct (96% - high mastery)
        attempts = (
            [{"correct": True} for _ in range(96)] +
            [{"correct": False} for _ in range(4)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["medium", "hard", "easy"]

        # 100 attempts, 85 correct (85% - strong)
        attempts = (
            [{"correct": True} for _ in range(85)] +
            [{"correct": False} for _ in range(15)]
        )
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy", "medium", "hard"]


class TestAdaptiveDifficultyEdgeCases:
    """Test edge cases in adaptive difficulty."""

    def test_all_correct_performance(self):
        """Test 100% accuracy."""
        # 5 attempts, all correct
        attempts = [{"correct": True} for _ in range(5)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy", "medium", "hard"]

        # 20 attempts, all correct (high mastery)
        attempts = [{"correct": True} for _ in range(20)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["medium", "hard", "easy"]

    def test_all_incorrect_performance(self):
        """Test 0% accuracy."""
        # 10 attempts, all incorrect
        attempts = [{"correct": False} for _ in range(10)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]

    def test_alternating_performance(self):
        """Test alternating correct/incorrect."""
        # 10 attempts, alternating (50%)
        attempts = [{"correct": i % 2 == 0} for i in range(10)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]

        # 20 attempts, alternating (50%)
        attempts = [{"correct": i % 2 == 0} for i in range(20)]
        sequence = _difficulty_sequence(attempts)
        assert sequence == ["easy"]
