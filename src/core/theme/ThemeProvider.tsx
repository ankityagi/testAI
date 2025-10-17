import React, { createContext, useContext, ReactNode } from 'react';
import { theme, Theme } from './index';

/**
 * Theme Context
 * Provides theme tokens to all components
 */

interface ThemeContextValue {
  theme: Theme;
  // Future: add toggleDarkMode, currentMode, etc.
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const value: ThemeContextValue = {
    theme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

/**
 * useTheme Hook
 * Access theme tokens in any component
 *
 * @example
 * const { theme } = useTheme();
 * const buttonColor = theme.colors.primary[500];
 */
export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
