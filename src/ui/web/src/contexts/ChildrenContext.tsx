/**
 * Children Context
 * Manages children list and selected child state
 */

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { childrenService } from '../services';
import type { Child, ChildCreate, ChildUpdate, ApiError } from '../types/api';

interface ChildrenContextType {
  children: Child[];
  selectedChild: Child | null;
  isLoading: boolean;
  error: string | null;
  fetchChildren: () => Promise<void>;
  selectChild: (child: Child | null) => void;
  addChild: (data: ChildCreate) => Promise<Child>;
  updateChild: (childId: string, data: ChildUpdate) => Promise<Child>;
  deleteChild: (childId: string) => Promise<void>;
  clearError: () => void;
}

const ChildrenContext = createContext<ChildrenContextType | undefined>(undefined);

interface ChildrenProviderProps {
  children: ReactNode;
}

export const ChildrenProvider: React.FC<ChildrenProviderProps> = ({ children }) => {
  const [childrenList, setChildrenList] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChildren = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await childrenService.list();
      setChildrenList(data);

      // If we have a selected child, update it with fresh data
      setSelectedChild((currentSelected) => {
        if (currentSelected) {
          const updatedChild = data.find((c) => c.id === currentSelected.id);
          return updatedChild || null;
        }
        return null;
      });
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to fetch children');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []); // ✅ No dependencies - stable reference

  const selectChild = useCallback((child: Child | null): void => {
    setSelectedChild(child);
    // Store selected child ID in localStorage for persistence
    if (child) {
      localStorage.setItem('selected_child_id', child.id);
    } else {
      localStorage.removeItem('selected_child_id');
    }
  }, []);

  const addChild = useCallback(async (data: ChildCreate): Promise<Child> => {
    try {
      setIsLoading(true);
      setError(null);
      const newChild = await childrenService.create(data);
      setChildrenList((prev) => [...prev, newChild]);
      return newChild;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to add child');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateChild = useCallback(async (childId: string, data: ChildUpdate): Promise<Child> => {
    try {
      setIsLoading(true);
      setError(null);
      const updatedChild = await childrenService.update(childId, data);
      setChildrenList((prev) => prev.map((c) => (c.id === childId ? updatedChild : c)));

      // Update selected child if it's the one being updated
      setSelectedChild((currentSelected) => {
        if (currentSelected?.id === childId) {
          return updatedChild;
        }
        return currentSelected;
      });

      return updatedChild;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to update child');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteChild = useCallback(async (childId: string): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      await childrenService.delete(childId);
      setChildrenList((prev) => prev.filter((c) => c.id !== childId));

      // Clear selected child if it's the one being deleted
      setSelectedChild((currentSelected) => {
        if (currentSelected?.id === childId) {
          return null;
        }
        return currentSelected;
      });
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to delete child');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []); // ✅ No dependencies - stable reference

  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  const value: ChildrenContextType = {
    children: childrenList,
    selectedChild,
    isLoading,
    error,
    fetchChildren,
    selectChild,
    addChild,
    updateChild,
    deleteChild,
    clearError,
  };

  return <ChildrenContext.Provider value={value}>{children}</ChildrenContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useChildren = (): ChildrenContextType => {
  const context = useContext(ChildrenContext);
  if (!context) {
    throw new Error('useChildren must be used within a ChildrenProvider');
  }
  return context;
};
