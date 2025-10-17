/**
 * Children Service
 * CRUD operations for managing children profiles
 */

import { apiClient } from './apiClient';
import type { Child, ChildCreate, ChildUpdate } from '../types/api';

export const childrenService = {
  /**
   * Get all children for authenticated parent
   */
  async list(): Promise<Child[]> {
    return apiClient.get<Child[]>('/children/');
  },

  /**
   * Create a new child
   */
  async create(data: ChildCreate): Promise<Child> {
    return apiClient.post<Child>('/children/', data);
  },

  /**
   * Get a specific child by ID
   */
  async get(childId: string): Promise<Child> {
    return apiClient.get<Child>(`/children/${childId}/`);
  },

  /**
   * Update a child's information
   */
  async update(childId: string, data: ChildUpdate): Promise<Child> {
    return apiClient.put<Child>(`/children/${childId}/`, data);
  },

  /**
   * Delete a child
   */
  async delete(childId: string): Promise<void> {
    return apiClient.delete<void>(`/children/${childId}/`);
  },
};
