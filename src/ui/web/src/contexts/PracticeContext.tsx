/**
 * Practice Context
 * Manages practice session state including current questions, answers, and progress
 */

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { questionsService, sessionsService } from '../services';
import type {
  Question,
  QuestionRequest,
  AttemptSubmission,
  AttemptResult,
  ApiError,
} from '../types/api';

interface QuestionState {
  question: Question;
  selectedAnswer: string | null;
  isAnswered: boolean;
  isCorrect: boolean | null;
  timeStarted: number;
}

interface PracticeContextType {
  // Session state
  questions: Question[];
  currentQuestionIndex: number;
  currentQuestion: QuestionState | null;
  selectedSubtopic: string | null;
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;

  // Session actions
  fetchQuestions: (request: QuestionRequest) => Promise<void>;
  selectAnswer: (answer: string) => void;
  submitAnswer: (childId: string) => Promise<AttemptResult | null>;
  nextQuestion: () => void;
  resetSession: () => void;
  endSession: () => Promise<void>;

  // Session stats
  questionsAnswered: number;
  correctAnswers: number;
  accuracy: number;

  clearError: () => void;
}

const PracticeContext = createContext<PracticeContextType | undefined>(undefined);

interface PracticeProviderProps {
  children: ReactNode;
}

export const PracticeProvider: React.FC<PracticeProviderProps> = ({ children }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionState | null>(null);
  const [selectedSubtopic, setSelectedSubtopic] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session stats
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);

  const accuracy =
    questionsAnswered > 0 ? Math.round((correctAnswers / questionsAnswered) * 100) : 0;

  const fetchQuestions = useCallback(async (request: QuestionRequest): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('[PracticeContext] Fetching questions with request:', request);
      const response = await questionsService.fetch(request);
      console.log('[PracticeContext] Received response:', {
        questionCount: response.questions.length,
        selectedSubtopic: response.selected_subtopic,
        sessionId: response.session_id,
        questions: response.questions.map(q => ({
          id: q.id,
          subject: q.subject,
          topic: q.topic,
          subtopic: q.subtopic,
          difficulty: q.difficulty,
          stem: q.stem.substring(0, 50) + '...',
        })),
      });

      setQuestions(response.questions);
      setSelectedSubtopic(response.selected_subtopic || null);
      setSessionId(response.session_id || null);

      // Initialize first question
      if (response.questions.length > 0) {
        setCurrentQuestionIndex(0);
        setCurrentQuestion({
          question: response.questions[0],
          selectedAnswer: null,
          isAnswered: false,
          isCorrect: null,
          timeStarted: Date.now(),
        });
        console.log('[PracticeContext] Initialized first question:', response.questions[0].stem);
      } else {
        setCurrentQuestion(null);
        console.log('[PracticeContext] No questions returned');
      }

      // Reset session stats
      setQuestionsAnswered(0);
      setCorrectAnswers(0);
    } catch (err) {
      const apiError = err as ApiError;
      console.error('[PracticeContext] Error fetching questions:', apiError);
      setError(apiError.detail || 'Failed to fetch questions');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectAnswer = useCallback(
    (answer: string): void => {
      if (currentQuestion && !currentQuestion.isAnswered) {
        setCurrentQuestion({
          ...currentQuestion,
          selectedAnswer: answer,
        });
      }
    },
    [currentQuestion]
  );

  const submitAnswer = useCallback(
    async (childId: string): Promise<AttemptResult | null> => {
      if (!currentQuestion || !currentQuestion.selectedAnswer) {
        return null;
      }

      try {
        setIsLoading(true);
        setError(null);

        const timeSpentMs = Date.now() - currentQuestion.timeStarted;
        const submission: AttemptSubmission = {
          child_id: childId,
          question_id: currentQuestion.question.id,
          selected: currentQuestion.selectedAnswer,
          time_spent_ms: timeSpentMs,
        };

        console.log('[PracticeContext] Submitting answer:', {
          questionId: currentQuestion.question.id,
          selected: currentQuestion.selectedAnswer,
          correctAnswer: currentQuestion.question.correct_answer,
          timeSpentMs,
        });

        const result = await questionsService.submitAttempt(submission);
        console.log('[PracticeContext] Answer result:', result);

        // Update current question state with result
        setCurrentQuestion({
          ...currentQuestion,
          isAnswered: true,
          isCorrect: result.correct,
        });

        // Update session stats
        setQuestionsAnswered((prev) => prev + 1);
        if (result.correct) {
          setCorrectAnswers((prev) => prev + 1);
        }

        // Dispatch event to notify other components (e.g., ProgressPanel) to refresh
        window.dispatchEvent(new CustomEvent('answer-submitted'));

        return result;
      } catch (err) {
        const apiError = err as ApiError;
        console.error('[PracticeContext] Error submitting answer:', apiError);
        setError(apiError.detail || 'Failed to submit answer');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [currentQuestion]
  );

  const nextQuestion = useCallback((): void => {
    const nextIndex = currentQuestionIndex + 1;
    if (nextIndex < questions.length) {
      setCurrentQuestionIndex(nextIndex);
      setCurrentQuestion({
        question: questions[nextIndex],
        selectedAnswer: null,
        isAnswered: false,
        isCorrect: null,
        timeStarted: Date.now(),
      });
    } else {
      // No more questions
      setCurrentQuestion(null);
    }
  }, [currentQuestionIndex, questions]);

  const endSession = useCallback(async (): Promise<void> => {
    if (!sessionId) {
      console.warn('[PracticeContext] No active session to end');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      console.log('[PracticeContext] Ending session:', sessionId);
      await sessionsService.endSession(sessionId);
      console.log('[PracticeContext] Session ended successfully');
    } catch (err) {
      const apiError = err as ApiError;
      console.error('[PracticeContext] Error ending session:', apiError);
      setError(apiError.detail || 'Failed to end session');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const resetSession = useCallback((): void => {
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setCurrentQuestion(null);
    setSelectedSubtopic(null);
    setSessionId(null);
    setQuestionsAnswered(0);
    setCorrectAnswers(0);
    setError(null);
  }, []);

  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  const value: PracticeContextType = {
    questions,
    currentQuestionIndex,
    currentQuestion,
    selectedSubtopic,
    sessionId,
    isLoading,
    error,
    fetchQuestions,
    selectAnswer,
    submitAnswer,
    nextQuestion,
    resetSession,
    endSession,
    questionsAnswered,
    correctAnswers,
    accuracy,
    clearError,
  };

  return <PracticeContext.Provider value={value}>{children}</PracticeContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const usePractice = (): PracticeContextType => {
  const context = useContext(PracticeContext);
  if (!context) {
    throw new Error('usePractice must be used within a PracticeProvider');
  }
  return context;
};
