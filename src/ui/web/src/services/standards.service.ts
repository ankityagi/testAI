/**
 * Standards Service
 * Fetch Common Core and other educational standards
 */

import { apiClient } from './apiClient';
import type { Standard } from '../types/api';

export const standardsService = {
  /**
   * Get all available standards
   */
  async list(): Promise<Standard[]> {
    return apiClient.get<Standard[]>('/standards');
  },

  /**
   * Filter standards by subject
   */
  filterBySubject(standards: Standard[], subject: string): Standard[] {
    return standards.filter((s) => s.subject.toLowerCase() === subject.toLowerCase());
  },

  /**
   * Filter standards by grade
   */
  filterByGrade(standards: Standard[], grade: number): Standard[] {
    return standards.filter((s) => s.grade === grade);
  },

  /**
   * Group standards by subject
   */
  groupBySubject(standards: Standard[]): Record<string, Standard[]> {
    return standards.reduce(
      (acc, standard) => {
        const subject = standard.subject;
        if (!acc[subject]) {
          acc[subject] = [];
        }
        acc[subject].push(standard);
        return acc;
      },
      {} as Record<string, Standard[]>
    );
  },

  /**
   * Group standards by grade
   */
  groupByGrade(standards: Standard[]): Record<number, Standard[]> {
    return standards.reduce(
      (acc, standard) => {
        const grade = standard.grade;
        if (!acc[grade]) {
          acc[grade] = [];
        }
        acc[grade].push(standard);
        return acc;
      },
      {} as Record<number, Standard[]>
    );
  },

  /**
   * Group standards by subject, then by grade
   */
  groupBySubjectAndGrade(standards: Standard[]): Record<string, Record<number, Standard[]>> {
    return standards.reduce(
      (acc, standard) => {
        const subject = standard.subject;
        const grade = standard.grade;

        if (!acc[subject]) {
          acc[subject] = {};
        }
        if (!acc[subject][grade]) {
          acc[subject][grade] = [];
        }
        acc[subject][grade].push(standard);
        return acc;
      },
      {} as Record<string, Record<number, Standard[]>>
    );
  },
};
