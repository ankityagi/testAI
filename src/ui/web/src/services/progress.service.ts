/**
 * Progress Service
 * Fetch progress and analytics for a child
 */

import { apiClient } from './apiClient';
import type { ProgressResponse } from '../types/api';

export const progressService = {
  /**
   * Get progress data for a specific child
   */
  async get(childId: string): Promise<ProgressResponse> {
    return apiClient.get<ProgressResponse>(`/progress/${childId}`);
  },

  /**
   * Calculate accuracy percentage
   */
  calculateAccuracy(correct: number, total: number): number {
    if (total === 0) return 0;
    return Math.round((correct / total) * 100);
  },

  /**
   * Format streak text for display
   */
  formatStreakText(streak: number): string {
    if (streak === 0) return 'No streak yet';
    if (streak === 1) return '1 day streak';
    return `${streak} day streak`;
  },

  /**
   * Get subject color for visualizations
   */
  getSubjectColor(subject: string): string {
    const colors: Record<string, string> = {
      math: '#FF9500',
      reading: '#AF52DE',
      science: '#34C759',
      writing: '#007AFF',
    };
    return colors[subject] || '#8E8E93';
  },
};
