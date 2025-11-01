/**
 * Quiz Context
 * Manages quiz session state including all questions, answers, timer, and submission
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  type ReactNode,
} from 'react';
import { quizService } from '../services';
import type {
  QuizCreateRequest,
  QuizSessionResponse,
  QuizQuestionDisplay,
  QuizResult,
  QuizSession,
  ApiError,
} from '../types/api';

interface QuizContextType {
  // Session state
  session: QuizSession | null;
  questions: QuizQuestionDisplay[];
  answers: Record<string, string>; // questionId -> selectedChoice
  timeRemaining: number | null; // seconds
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  result: QuizResult | null;

  // Actions
  createQuiz: (request: QuizCreateRequest) => Promise<void>;
  selectAnswer: (questionId: string, choice: string) => void;
  submitQuiz: () => Promise<void>;
  loadQuiz: (sessionId: string) => Promise<void>;
  resetQuiz: () => void;
  clearError: () => void;

  // Timer info
  isExpired: boolean;
  percentTimeRemaining: number;
}

const QuizContext = createContext<QuizContextType | undefined>(undefined);

interface QuizProviderProps {
  children: ReactNode;
}

export const QuizProvider: React.FC<QuizProviderProps> = ({ children }) => {
  const [session, setSession] = useState<QuizSession | null>(null);
  const [questions, setQuestions] = useState<QuizQuestionDisplay[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QuizResult | null>(null);

  const timerIntervalRef = useRef<number | null>(null);
  const syncIntervalRef = useRef<number | null>(null);
  const lastSyncRef = useRef<number>(Date.now());

  // Calculate time remaining locally
  const isExpired = timeRemaining !== null && timeRemaining <= 0;
  const percentTimeRemaining =
    session && timeRemaining !== null
      ? Math.max(0, Math.min(100, (timeRemaining / session.duration_sec) * 100))
      : 100;

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, []);

  // Auto-submit when time expires
  useEffect(() => {
    if (isExpired && session && session.status === 'active' && !isSubmitting) {
      console.log('[QuizContext] Time expired, auto-submitting quiz');
      submitQuiz();
    }
  }, [isExpired, session, isSubmitting, submitQuiz]);

  // Start timer countdown (local, 1s intervals)
  const startLocalTimer = useCallback(() => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }

    timerIntervalRef.current = window.setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev === null || prev <= 0) {
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  // Sync time with backend every 10s
  const syncTimeWithBackend = useCallback(
    async (sessionId: string) => {
      try {
        const now = Date.now();
        const timeSinceLastSync = (now - lastSyncRef.current) / 1000;

        // Only sync if it's been at least 9s (allows some drift)
        if (timeSinceLastSync < 9) {
          return;
        }

        console.log('[QuizContext] Syncing time with backend...');
        const response = await quizService.get(sessionId);

        if (response.time_remaining_sec !== undefined && response.time_remaining_sec !== null) {
          setTimeRemaining(response.time_remaining_sec);
          console.log('[QuizContext] Time synced:', response.time_remaining_sec, 's remaining');
        }

        lastSyncRef.current = now;
      } catch (err) {
        console.error('[QuizContext] Failed to sync time:', err);
        // Don't set error state for sync failures, timer continues locally
      }
    },
    []
  );

  // Start backend sync interval (every 10s)
  const startBackendSync = useCallback(
    (sessionId: string) => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }

      syncIntervalRef.current = window.setInterval(() => {
        syncTimeWithBackend(sessionId);
      }, 10000);
    },
    [syncTimeWithBackend]
  );

  const createQuiz = useCallback(
    async (request: QuizCreateRequest): Promise<void> => {
      try {
        setIsLoading(true);
        setError(null);
        setResult(null);

        console.log('[QuizContext] Creating quiz with request:', request);
        const response: QuizSessionResponse = await quizService.create(request);
        console.log('[QuizContext] Quiz created:', {
          sessionId: response.session.id,
          questionCount: response.questions.length,
          duration: response.session.duration_sec,
        });

        setSession(response.session);
        setQuestions(response.questions);
        setAnswers({});
        setTimeRemaining(response.time_remaining_sec || response.session.duration_sec);

        // Start timers
        startLocalTimer();
        startBackendSync(response.session.id);
        lastSyncRef.current = Date.now();
      } catch (err) {
        const apiError = err as ApiError;
        console.error('[QuizContext] Error creating quiz:', apiError);
        setError(apiError.detail || 'Failed to create quiz');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [startLocalTimer, startBackendSync]
  );

  const loadQuiz = useCallback(
    async (sessionId: string): Promise<void> => {
      try {
        setIsLoading(true);
        setError(null);

        console.log('[QuizContext] Loading quiz:', sessionId);
        const response: QuizSessionResponse = await quizService.get(sessionId);
        console.log('[QuizContext] Quiz loaded:', {
          status: response.session.status,
          questionCount: response.questions.length,
        });

        setSession(response.session);
        setQuestions(response.questions);
        setTimeRemaining(response.time_remaining_sec || 0);

        // Only start timers if quiz is still active
        if (response.session.status === 'active') {
          startLocalTimer();
          startBackendSync(sessionId);
          lastSyncRef.current = Date.now();
        }
      } catch (err) {
        const apiError = err as ApiError;
        console.error('[QuizContext] Error loading quiz:', apiError);
        setError(apiError.detail || 'Failed to load quiz');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [startLocalTimer, startBackendSync]
  );

  const selectAnswer = useCallback((questionId: string, choice: string): void => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: choice,
    }));
    console.log('[QuizContext] Answer selected:', { questionId, choice });
  }, []);

  const submitQuiz = useCallback(async (): Promise<void> => {
    if (!session) {
      console.warn('[QuizContext] No active session to submit');
      return;
    }

    if (isSubmitting) {
      console.warn('[QuizContext] Submit already in progress');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      // Stop timers
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
        syncIntervalRef.current = null;
      }

      // Build submission from answers
      const submission = {
        answers: questions.map((q) => ({
          question_id: q.id,
          selected_choice: answers[q.id] || '', // Empty string for unanswered
        })),
      };

      console.log('[QuizContext] Submitting quiz:', {
        sessionId: session.id,
        totalQuestions: questions.length,
        answered: Object.keys(answers).length,
      });

      const quizResult = await quizService.submit(session.id, submission);
      console.log('[QuizContext] Quiz graded:', {
        score: quizResult.score,
        correct: quizResult.correct_count,
        total: quizResult.total_questions,
      });

      setResult(quizResult);

      // Update session status
      setSession((prev) =>
        prev
          ? {
              ...prev,
              status: 'completed',
              score: quizResult.score,
              submitted_at: quizResult.submitted_at,
            }
          : null
      );
    } catch (err) {
      const apiError = err as ApiError;
      console.error('[QuizContext] Error submitting quiz:', apiError);
      setError(apiError.detail || 'Failed to submit quiz');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  }, [session, questions, answers, isSubmitting]);

  const resetQuiz = useCallback((): void => {
    // Stop timers
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
      syncIntervalRef.current = null;
    }

    setSession(null);
    setQuestions([]);
    setAnswers({});
    setTimeRemaining(null);
    setResult(null);
    setError(null);
    console.log('[QuizContext] Quiz reset');
  }, []);

  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  const value: QuizContextType = {
    session,
    questions,
    answers,
    timeRemaining,
    isLoading,
    isSubmitting,
    error,
    result,
    createQuiz,
    selectAnswer,
    submitQuiz,
    loadQuiz,
    resetQuiz,
    clearError,
    isExpired,
    percentTimeRemaining,
  };

  return <QuizContext.Provider value={value}>{children}</QuizContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useQuiz = (): QuizContextType => {
  const context = useContext(QuizContext);
  if (!context) {
    throw new Error('useQuiz must be used within a QuizProvider');
  }
  return context;
};
