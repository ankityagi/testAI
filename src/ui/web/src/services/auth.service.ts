/**
 * Authentication Service
 * Handles signup, login, logout operations
 */

import { apiClient } from './apiClient';
import type { AuthRequest, AuthResponse } from '../types/api';

export const authService = {
  /**
   * Sign up a new parent account
   */
  async signup(email: string, password: string): Promise<AuthResponse> {
    const request: AuthRequest = { email, password };
    const response = await apiClient.post<AuthResponse>('/auth/signup', request);

    // Store token in API client
    apiClient.setToken(response.access_token);

    return response;
  },

  /**
   * Log in to existing account
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const request: AuthRequest = { email, password };
    const response = await apiClient.post<AuthResponse>('/auth/login', request);

    // Store token in API client
    apiClient.setToken(response.access_token);

    return response;
  },

  /**
   * Log out current user
   */
  logout(): void {
    apiClient.clearToken();
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return apiClient.isAuthenticated();
  },

  /**
   * Get current auth token
   */
  getToken(): string | null {
    return apiClient.getToken();
  },
};
