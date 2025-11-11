/**
 * Dashboard Page
 * Main application layout with header, navigation, and panels
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { theme } from '../../../../core/theme';
import { useAuth, useChildren, useQuiz } from '../contexts';
import { Button, Card, QuizSetupModal } from '../components';
import { ChildrenPanel, PracticePanel, ProgressPanel } from '../components/panels';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { parent, logout } = useAuth();
  const { children, selectedChild, fetchChildren } = useChildren();
  const { session } = useQuiz();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [showQuizSetup, setShowQuizSetup] = useState(false);

  // Fetch children on mount
  useEffect(() => {
    fetchChildren();
  }, [fetchChildren]);

  // Trigger stagger animation on mount
  useEffect(() => {
    setIsAnimating(true);
  }, []);

  // Navigate to quiz when session is created
  useEffect(() => {
    if (session && session.status === 'active') {
      navigate(`/quiz/${session.id}`);
    }
  }, [session, navigate]);

  const handleLogout = (): void => {
    logout();
    navigate('/auth');
  };

  const handleQuizSetupClose = (): void => {
    setShowQuizSetup(false);
  };

  const containerStyles: React.CSSProperties = {
    minHeight: '100vh',
    backgroundColor: theme.colors.background.secondary,
    opacity: isAnimating ? 1 : 0,
    transform: isAnimating ? 'translateY(0)' : 'translateY(10px)',
    transition: 'opacity 0.5s ease-out, transform 0.5s ease-out',
  };

  const headerStyles: React.CSSProperties = {
    borderBottom: `1px solid ${theme.colors.border.light}`,
    padding: `${theme.spacing[4]} ${theme.spacing[6]}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    backdropFilter: 'blur(10px)',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
  };

  const logoStyles: React.CSSProperties = {
    ...theme.typography.styles.h2,
    fontSize: theme.typography.fontSize['2xl'],
    background: theme.colors.gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    margin: 0,
  };

  const userSectionStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[4],
    position: 'relative',
  };

  const userInfoStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[3],
    cursor: 'pointer',
    padding: theme.spacing[2],
    borderRadius: theme.borderRadius.md,
    transition: theme.animations.transition.all,
  };

  const avatarStyles: React.CSSProperties = {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: theme.colors.gradients.primary,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: theme.colors.text.inverse,
    fontWeight: theme.typography.fontWeight.semibold,
    fontSize: theme.typography.fontSize.lg,
  };

  const userMenuStyles: React.CSSProperties = {
    position: 'absolute',
    top: '100%',
    right: 0,
    marginTop: theme.spacing[2],
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.md,
    boxShadow: theme.shadows.lg,
    padding: theme.spacing[2],
    minWidth: '200px',
    opacity: showUserMenu ? 1 : 0,
    transform: showUserMenu ? 'scale(1)' : 'scale(0.95)',
    transformOrigin: 'top right',
    transition: theme.animations.transition.all,
    pointerEvents: showUserMenu ? 'auto' : 'none',
  };

  const mainContentStyles: React.CSSProperties = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: theme.spacing[6],
  };

  const welcomeStyles: React.CSSProperties = {
    marginBottom: theme.spacing[8],
  };

  const welcomeTextStyles: React.CSSProperties = {
    ...theme.typography.styles.h1,
    fontSize: theme.typography.fontSize['3xl'],
    marginBottom: theme.spacing[2],
  };

  const subtitleStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
  };

  const gridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'minmax(280px, 320px) minmax(400px, 1.5fr) minmax(350px, 1fr)',
    gap: theme.spacing[6],
  };

  const emptyStateStyles: React.CSSProperties = {
    textAlign: 'center',
    padding: theme.spacing[12],
  };

  const emptyIconStyles: React.CSSProperties = {
    fontSize: '64px',
    marginBottom: theme.spacing[4],
  };

  const getInitials = (email: string): string => {
    return email.charAt(0).toUpperCase();
  };

  return (
    <div style={containerStyles}>
      {/* Header */}
      <header style={headerStyles}>
        <h1 style={logoStyles}>StudyBuddy</h1>

        <div style={userSectionStyles}>
          <div
            style={userInfoStyles}
            onClick={() => setShowUserMenu(!showUserMenu)}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.background.secondary;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <div style={avatarStyles}>{parent ? getInitials(parent.email) : '?'}</div>
            <div>
              <div style={{ fontWeight: theme.typography.fontWeight.medium }}>{parent?.email}</div>
              <div
                style={{
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.text.secondary,
                }}
              >
                {children.length} {children.length === 1 ? 'child' : 'children'}
              </div>
            </div>
          </div>

          {/* User menu dropdown */}
          <div style={userMenuStyles}>
            <Button variant="ghost" fullWidth onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={mainContentStyles}>
        <div style={welcomeStyles}>
          <h2 style={welcomeTextStyles}>
            Welcome back{parent && `, ${parent.email.split('@')[0]}`}!
          </h2>
          <p style={subtitleStyles}>
            {selectedChild
              ? `Currently viewing progress for ${selectedChild.name}`
              : 'Select a child to get started'}
          </p>
        </div>

        {children.length === 0 ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 400px) 1fr',
            gap: theme.spacing[6],
            alignItems: 'start',
          }}>
            {/* Add Child panel on the left */}
            <Card header="Add Your First Child" headerGradient>
              <ChildrenPanel />
            </Card>

            {/* Welcome panel on the right */}
            <Card>
              <div style={emptyStateStyles}>
                <div style={emptyIconStyles}>👋</div>
                <h3 style={theme.typography.styles.h3}>Welcome to StudyBuddy!</h3>
                <p
                  style={{
                    color: theme.colors.text.secondary,
                    marginBottom: theme.spacing[4],
                  }}
                >
                  Get started by adding your first child to begin their learning journey.
                </p>
              </div>
            </Card>
          </div>
        ) : (
          <>
            {/* Quiz Mode Section */}
            {selectedChild && (
              <div style={{ marginBottom: theme.spacing[6] }}>
                <Card>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: theme.spacing[4],
                  }}>
                    <div>
                      <h3 style={{
                        ...theme.typography.styles.h3,
                        marginBottom: theme.spacing[2],
                      }}>
                        Quiz Mode
                      </h3>
                      <p style={{
                        color: theme.colors.text.secondary,
                        fontSize: theme.typography.fontSize.base,
                      }}>
                        Test your knowledge with timed quizzes on specific topics
                      </p>
                    </div>
                    <Button
                      size="lg"
                      onClick={() => setShowQuizSetup(true)}
                    >
                      Start Quiz
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            <div style={gridStyles}>
              <Card header="Children" headerGradient>
                <ChildrenPanel />
              </Card>

              {selectedChild && (
                <>
                  <Card header="Practice" headerGradient>
                    <PracticePanel />
                  </Card>

                  <Card header="Progress" headerGradient>
                    <ProgressPanel />
                  </Card>
                </>
              )}
            </div>
          </>
        )}

        {/* Quiz Setup Modal */}
        <QuizSetupModal isOpen={showQuizSetup} onClose={handleQuizSetupClose} />
      </main>
    </div>
  );
};
