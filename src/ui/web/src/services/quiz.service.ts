/**
 * Quiz Service
 * API operations for quiz mode - timed assessments with fixed question sets
 */

import { apiClient } from './apiClient';
import type {
  QuizCreateRequest,
  QuizSession,
  QuizSessionResponse,
  QuizSubmitRequest,
  QuizResult,
} from '../types/api';

export const quizService = {
  /**
   * Create a new quiz session
   * Returns session with questions (answers hidden)
   */
  async create(data: QuizCreateRequest): Promise<QuizSessionResponse> {
    return apiClient.post<QuizSessionResponse>('/quiz/sessions/', data);
  },

  /**
   * List quiz sessions for a child
   */
  async list(childId: string, limit = 20, offset = 0): Promise<QuizSession[]> {
    return apiClient.get<QuizSession[]>('/quiz/sessions/', {
      params: { child_id: childId, limit, offset },
    });
  },

  /**
   * Get a specific quiz session by ID
   * Returns remaining time and questions (answers hidden if not submitted)
   */
  async get(sessionId: string): Promise<QuizSessionResponse> {
    return apiClient.get<QuizSessionResponse>(`/quiz/sessions/${sessionId}/`);
  },

  /**
   * Submit quiz answers for grading
   * Returns score and incorrect items with explanations
   */
  async submit(sessionId: string, data: QuizSubmitRequest): Promise<QuizResult> {
    return apiClient.post<QuizResult>(`/quiz/sessions/${sessionId}/submit/`, data);
  },

  /**
   * Manually expire a quiz session
   */
  async expire(sessionId: string): Promise<QuizSession> {
    return apiClient.post<QuizSession>(`/quiz/sessions/${sessionId}/expire/`, {});
  },
};
