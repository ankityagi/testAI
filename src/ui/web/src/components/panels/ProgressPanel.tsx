/**
 * Progress Panel Component
 * Displays child progress statistics and subject breakdown
 */

import React, { useEffect, useState, useCallback } from 'react';
import { theme } from '../../../../../core/theme';
import { useChildren } from '../../contexts';
import { LoadingSpinner, Toast } from '..';
import { progressService } from '../../services';
import type { ProgressResponse, ApiError } from '../../types/api';

export const ProgressPanel: React.FC = () => {
  const { selectedChild } = useChildren();
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProgress = useCallback(async (): Promise<void> => {
    if (!selectedChild) {
      setProgress(null);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const data = await progressService.get(selectedChild.id);
      setProgress(data);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.detail || 'Failed to load progress');
    } finally {
      setIsLoading(false);
    }
  }, [selectedChild]);

  // Fetch progress on mount and when selected child changes
  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  // Listen for answer submission events to refresh progress
  useEffect(() => {
    const handleAnswerSubmitted = (): void => {
      console.log('[ProgressPanel] Answer submitted event received, refreshing progress...');
      fetchProgress();
    };

    window.addEventListener('answer-submitted', handleAnswerSubmitted);

    return () => {
      window.removeEventListener('answer-submitted', handleAnswerSubmitted);
    };
  }, [fetchProgress]);

  // Styles
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const overviewStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: theme.spacing[4],
  };

  const statCardStyles: React.CSSProperties = {
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    textAlign: 'center',
  };

  const statValueStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    background: theme.colors.gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: theme.spacing[1],
  };

  const statLabelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  };

  const streakStyles: React.CSSProperties = {
    padding: theme.spacing[4],
    backgroundColor: theme.colors.primary[50],
    borderRadius: theme.borderRadius.md,
    textAlign: 'center',
    border: `1px solid ${theme.colors.primary[200]}`,
  };

  const streakValueStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize['4xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.primary[600],
    marginBottom: theme.spacing[2],
  };

  const streakLabelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.primary[700],
  };

  const subjectSectionStyles: React.CSSProperties = {
    marginTop: theme.spacing[2],
  };

  const subjectHeaderStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    marginBottom: theme.spacing[3],
  };

  const subjectListStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  };

  const subjectItemStyles: React.CSSProperties = {
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
  };

  const subjectNameStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    marginBottom: theme.spacing[2],
    textTransform: 'capitalize',
  };

  const subjectStatsStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing[2],
  };

  const subjectStatTextStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  };

  const progressBarContainerStyles: React.CSSProperties = {
    height: '8px',
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.full,
    overflow: 'hidden',
  };

  const progressBarFillStyles = (accuracy: number, subject: string): React.CSSProperties => ({
    height: '100%',
    width: `${accuracy}%`,
    backgroundColor: progressService.getSubjectColor(subject),
    transition: theme.animations.transition.all,
    borderRadius: theme.borderRadius.full,
  });

  const emptyStateStyles: React.CSSProperties = {
    textAlign: 'center',
    padding: theme.spacing[8],
    color: theme.colors.text.secondary,
  };

  const emptyIconStyles: React.CSSProperties = {
    fontSize: '48px',
    marginBottom: theme.spacing[3],
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: theme.spacing[6] }}>
        <LoadingSpinner size="md" label="Loading progress..." />
      </div>
    );
  }

  if (!selectedChild) {
    return (
      <div style={emptyStateStyles}>
        <div style={emptyIconStyles}>👈</div>
        <p>Select a child to view their progress</p>
      </div>
    );
  }

  if (!progress || progress.attempted === 0) {
    return (
      <div style={emptyStateStyles}>
        <div style={emptyIconStyles}>📊</div>
        <p>No practice data yet</p>
        <p style={{ fontSize: theme.typography.fontSize.sm, marginTop: theme.spacing[2] }}>
          Start practicing to see progress here!
        </p>
      </div>
    );
  }

  return (
    <div style={containerStyles}>
      {/* Overview Stats */}
      <div style={overviewStyles}>
        <div style={statCardStyles}>
          <div style={statValueStyles}>{progress.attempted}</div>
          <div style={statLabelStyles}>Questions</div>
        </div>

        <div style={statCardStyles}>
          <div style={statValueStyles}>{progress.correct}</div>
          <div style={statLabelStyles}>Correct</div>
        </div>

        <div style={statCardStyles}>
          <div style={statValueStyles}>{progress.accuracy}%</div>
          <div style={statLabelStyles}>Accuracy</div>
        </div>
      </div>

      {/* Streak */}
      {progress.current_streak > 0 && (
        <div style={streakStyles}>
          <div style={streakValueStyles}>🔥 {progress.current_streak}</div>
          <div style={streakLabelStyles}>
            {progressService.formatStreakText(progress.current_streak)}
          </div>
        </div>
      )}

      {/* Subject Breakdown */}
      {Object.keys(progress.by_subject).length > 0 && (
        <div style={subjectSectionStyles}>
          <h4 style={subjectHeaderStyles}>By Subject</h4>

          <div style={subjectListStyles}>
            {Object.entries(progress.by_subject).map(([subject, data]) => (
              <div key={subject} style={subjectItemStyles}>
                <div style={subjectNameStyles}>{subject}</div>

                <div style={subjectStatsStyles}>
                  <span style={subjectStatTextStyles}>
                    {data.correct} / {data.total} correct
                  </span>
                  <span
                    style={{
                      ...subjectStatTextStyles,
                      fontWeight: theme.typography.fontWeight.semibold,
                      color: theme.colors.text.primary,
                    }}
                  >
                    {data.accuracy}%
                  </span>
                </div>

                <div style={progressBarContainerStyles}>
                  <div style={progressBarFillStyles(data.accuracy, subject)} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <Toast message={error} variant="error" onDismiss={() => setError(null)} />}
    </div>
  );
};
