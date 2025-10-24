/**
 * Main App Component
 * Sets up routing and global providers
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, ChildrenProvider, PracticeProvider } from './contexts';
import { ProtectedRoute } from './components';
import { Auth, Dashboard, ThemeDemo } from './pages';
import { SessionSummary } from './pages/SessionSummary';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ChildrenProvider>
          <PracticeProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/auth" element={<Auth />} />
              <Route path="/theme-demo" element={<ThemeDemo />} />

              {/* Protected routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/session/:sessionId/summary"
                element={
                  <ProtectedRoute>
                    <SessionSummary />
                  </ProtectedRoute>
                }
              />

              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </PracticeProvider>
        </ChildrenProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
