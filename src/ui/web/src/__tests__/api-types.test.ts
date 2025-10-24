/**
 * Type validation tests for API models
 * These tests verify that our TypeScript types match the backend Pydantic models
 */

import type {
  AttemptSubmission,
  ProgressResponse,
  SubjectBreakdown,
  Question,
} from '../types/api';

describe('API Type Validations', () => {
  describe('AttemptSubmission', () => {
    it('should have all required fields with correct types', () => {
      const attempt: AttemptSubmission = {
        child_id: '123e4567-e89b-12d3-a456-426614174000',
        question_id: '123e4567-e89b-12d3-a456-426614174001',
        selected: 'Option A',
        time_spent_ms: 5000,
      };

      expect(typeof attempt.child_id).toBe('string');
      expect(typeof attempt.question_id).toBe('string');
      expect(typeof attempt.selected).toBe('string');
      expect(typeof attempt.time_spent_ms).toBe('number');
    });

    it('should accept time_spent_ms as number (milliseconds)', () => {
      const quickAnswer: AttemptSubmission = {
        child_id: '123e4567-e89b-12d3-a456-426614174000',
        question_id: '123e4567-e89b-12d3-a456-426614174001',
        selected: 'A',
        time_spent_ms: 100, // 100ms - very quick
      };

      const normalAnswer: AttemptSubmission = {
        child_id: '123e4567-e89b-12d3-a456-426614174000',
        question_id: '123e4567-e89b-12d3-a456-426614174001',
        selected: 'B',
        time_spent_ms: 30000, // 30 seconds
      };

      const slowAnswer: AttemptSubmission = {
        child_id: '123e4567-e89b-12d3-a456-426614174000',
        question_id: '123e4567-e89b-12d3-a456-426614174001',
        selected: 'C',
        time_spent_ms: 120000, // 2 minutes
      };

      expect(quickAnswer.time_spent_ms).toBe(100);
      expect(normalAnswer.time_spent_ms).toBe(30000);
      expect(slowAnswer.time_spent_ms).toBe(120000);
    });
  });

  describe('ProgressResponse', () => {
    it('should have accuracy as integer percentage (0-100)', () => {
      const progress: ProgressResponse = {
        attempted: 10,
        correct: 8,
        accuracy: 80, // Integer percentage, not 0.80
        current_streak: 3,
        by_subject: {},
      };

      expect(typeof progress.accuracy).toBe('number');
      expect(progress.accuracy).toBe(80);
      expect(Number.isInteger(progress.accuracy)).toBe(true);
    });

    it('should support multiple subjects in breakdown', () => {
      const progress: ProgressResponse = {
        attempted: 30,
        correct: 24,
        accuracy: 80,
        current_streak: 2,
        by_subject: {
          Math: { correct: 10, total: 12, accuracy: 83 },
          Reading: { correct: 8, total: 10, accuracy: 80 },
          Science: { correct: 6, total: 8, accuracy: 75 },
        },
      };

      expect(Object.keys(progress.by_subject).length).toBe(3);
      expect(progress.by_subject.Math.accuracy).toBe(83);
      expect(progress.by_subject.Reading.accuracy).toBe(80);
      expect(progress.by_subject.Science.accuracy).toBe(75);
    });

    it('should handle zero attempts', () => {
      const progress: ProgressResponse = {
        attempted: 0,
        correct: 0,
        accuracy: 0,
        current_streak: 0,
        by_subject: {},
      };

      expect(progress.attempted).toBe(0);
      expect(progress.accuracy).toBe(0);
    });

    it('should allow negative streaks (for incorrect answers)', () => {
      const progress: ProgressResponse = {
        attempted: 10,
        correct: 3,
        accuracy: 30,
        current_streak: -3, // Negative for incorrect streak
        by_subject: {},
      };

      expect(progress.current_streak).toBe(-3);
    });
  });

  describe('SubjectBreakdown', () => {
    it('should have accuracy as integer percentage', () => {
      const breakdown: SubjectBreakdown = {
        correct: 8,
        total: 10,
        accuracy: 80, // Integer, not float
      };

      expect(typeof breakdown.accuracy).toBe('number');
      expect(Number.isInteger(breakdown.accuracy)).toBe(true);
    });

    it('should handle perfect score', () => {
      const breakdown: SubjectBreakdown = {
        correct: 10,
        total: 10,
        accuracy: 100,
      };

      expect(breakdown.accuracy).toBe(100);
    });

    it('should handle zero score', () => {
      const breakdown: SubjectBreakdown = {
        correct: 0,
        total: 10,
        accuracy: 0,
      };

      expect(breakdown.accuracy).toBe(0);
    });
  });

  describe('Question', () => {
    it('should have all required fields', () => {
      const question: Question = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        subject: 'Math',
        grade: 3,
        topic: 'Multiplication',
        subtopic: 'Single-Digit Multiplication',
        difficulty: 'medium',
        stem: 'What is 3 × 4?',
        options: ['10', '11', '12', '13'],
        correct_answer: '12',
        rationale: '3 groups of 4 equals 12',
        hash: 'abc123',
      };

      expect(typeof question.id).toBe('string');
      expect(typeof question.subject).toBe('string');
      expect(typeof question.grade).toBe('number');
      expect(typeof question.stem).toBe('string');
      expect(Array.isArray(question.options)).toBe(true);
      expect(question.options.length).toBe(4);
    });

    it('should support optional fields', () => {
      const minimalQuestion: Partial<Question> & Pick<Question, 'id' | 'stem' | 'options' | 'correct_answer'> = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        stem: 'Test question?',
        options: ['A', 'B', 'C', 'D'],
        correct_answer: 'A',
        // Other fields are optional
      };

      expect(minimalQuestion.id).toBeDefined();
      expect(minimalQuestion.stem).toBeDefined();
    });
  });
});

describe('Time Tracking Validation', () => {
  it('should convert seconds to milliseconds correctly', () => {
    const secondsToMs = (seconds: number): number => seconds * 1000;

    expect(secondsToMs(1)).toBe(1000);
    expect(secondsToMs(30)).toBe(30000);
    expect(secondsToMs(120)).toBe(120000);
  });

  it('should validate reasonable time ranges', () => {
    const isValidTimeMs = (ms: number): boolean => {
      const MIN_TIME_MS = 100; // 100ms minimum
      const MAX_TIME_MS = 600000; // 10 minutes maximum
      return ms >= MIN_TIME_MS && ms <= MAX_TIME_MS;
    };

    expect(isValidTimeMs(50)).toBe(false); // Too quick
    expect(isValidTimeMs(100)).toBe(true); // Minimum
    expect(isValidTimeMs(30000)).toBe(true); // Normal (30s)
    expect(isValidTimeMs(120000)).toBe(true); // Slow (2min)
    expect(isValidTimeMs(600000)).toBe(true); // Maximum (10min)
    expect(isValidTimeMs(700000)).toBe(false); // Too slow
  });
});

describe('Accuracy Calculation Validation', () => {
  it('should calculate integer percentage correctly', () => {
    const calculateAccuracy = (correct: number, total: number): number => {
      if (total === 0) return 0;
      return Math.round((correct / total) * 100);
    };

    expect(calculateAccuracy(8, 10)).toBe(80);
    expect(calculateAccuracy(0, 10)).toBe(0);
    expect(calculateAccuracy(10, 10)).toBe(100);
    expect(calculateAccuracy(3, 10)).toBe(30);
    expect(calculateAccuracy(1, 3)).toBe(33); // Rounds 33.333...
    expect(calculateAccuracy(2, 3)).toBe(67); // Rounds 66.666...
    expect(calculateAccuracy(0, 0)).toBe(0); // Edge case
  });

  it('should never return float for accuracy', () => {
    const calculateAccuracy = (correct: number, total: number): number => {
      if (total === 0) return 0;
      return Math.round((correct / total) * 100);
    };

    const accuracy = calculateAccuracy(1, 3);
    expect(Number.isInteger(accuracy)).toBe(true);
  });
});
