/**
 * Auth Context
 * Manages user authentication state and provides login/logout functionality
 */

import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authService } from '../services';
import type { Parent, ApiError } from '../types/api';

interface AuthContextType {
  parent: Parent | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [parent, setParent] = useState<Parent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      if (token) {
        // Token exists, but we need to verify it's valid
        // For now, we'll assume it's valid if it exists
        // In a real app, you'd verify with the backend
        setIsLoading(false);
      } else {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authService.login(email, password);
      setParent(response.parent);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await authService.signup(email, password);
      setParent(response.parent);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Signup failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = (): void => {
    authService.logout();
    setParent(null);
    setError(null);
  };

  const clearError = (): void => {
    setError(null);
  };

  const value: AuthContextType = {
    parent,
    isAuthenticated: !!parent,
    isLoading,
    login,
    signup,
    logout,
    error,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
