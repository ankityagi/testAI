/**
 * Sessions Service
 * Handles session tracking API requests
 */

import { apiClient } from './apiClient';
import type { Session, SessionSummary } from '../types/api';

class SessionsService {
  /**
   * Get session details
   */
  async getSession(sessionId: string): Promise<Session> {
    return apiClient.get<Session>(`/sessions/${sessionId}`);
  }

  /**
   * Get session summary with statistics
   */
  async getSessionSummary(sessionId: string): Promise<SessionSummary> {
    return apiClient.get<SessionSummary>(`/sessions/${sessionId}/summary`);
  }

  /**
   * End an active practice session
   */
  async endSession(sessionId: string): Promise<Session> {
    console.log('[SessionsService] Ending session with ID:', sessionId);
    console.log('[SessionsService] POST URL:', `/sessions/${sessionId}/end`);
    const result = await apiClient.post<Session>(`/sessions/${sessionId}/end`, {});
    console.log('[SessionsService] End session result:', result);
    return result;
  }
}

export const sessionsService = new SessionsService();
