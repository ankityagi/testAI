/**
 * Session Summary Page
 * Displays end-of-session statistics and performance metrics
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { theme } from '../../../../core/theme';
import { sessionsService } from '../services';
import { Button, Card } from '../components';
import type { SessionSummary as SessionSummaryType } from '../types/api';

export const SessionSummary: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [summary, setSummary] = useState<SessionSummaryType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      if (!sessionId) {
        setError('No session ID provided');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const data = await sessionsService.getSessionSummary(sessionId);
        setSummary(data);
      } catch (err) {
        setError('Failed to load session summary');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, [sessionId]);

  const formatTime = (ms: number): string => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}m ${seconds}s`;
  };

  const containerStyles: React.CSSProperties = {
    minHeight: '100vh',
    backgroundColor: theme.colors.background.secondary,
    padding: theme.spacing[6],
  };

  const headerStyles: React.CSSProperties = {
    maxWidth: '800px',
    margin: '0 auto',
    marginBottom: theme.spacing[6],
  };

  const contentStyles: React.CSSProperties = {
    maxWidth: '800px',
    margin: '0 auto',
  };

  const titleStyles: React.CSSProperties = {
    ...theme.typography.styles.h1,
    fontSize: theme.typography.fontSize['3xl'],
    marginBottom: theme.spacing[2],
    textAlign: 'center',
  };

  const subtitleStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  };

  const statsGridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: theme.spacing[4],
    marginBottom: theme.spacing[6],
  };

  const statCardStyles: React.CSSProperties = {
    padding: theme.spacing[6],
    borderRadius: theme.borderRadius.lg,
    backgroundColor: theme.colors.background.primary,
    border: `1px solid ${theme.colors.border.light}`,
    textAlign: 'center',
  };

  const statValueStyles: React.CSSProperties = {
    ...theme.typography.styles.h1,
    fontSize: theme.typography.fontSize['4xl'],
    marginBottom: theme.spacing[2],
  };

  const statLabelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  const buttonGroupStyles: React.CSSProperties = {
    display: 'flex',
    gap: theme.spacing[4],
    justifyContent: 'center',
  };

  if (isLoading) {
    return (
      <div style={containerStyles}>
        <div style={{ textAlign: 'center', padding: theme.spacing[12] }}>
          <p>Loading session summary...</p>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div style={containerStyles}>
        <div style={{ textAlign: 'center', padding: theme.spacing[12] }}>
          <p style={{ color: theme.colors.error[500], marginBottom: theme.spacing[4] }}>
            {error || 'Session not found'}
          </p>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const accuracyColor =
    summary.accuracy >= 80
      ? theme.colors.success[500]
      : summary.accuracy >= 60
        ? theme.colors.warning[500]
        : theme.colors.error[500];

  return (
    <div style={containerStyles}>
      <div style={headerStyles}>
        <h1 style={titleStyles}>🎉 Great Work!</h1>
        <p style={subtitleStyles}>Here's how you did in this session</p>
      </div>

      <div style={contentStyles}>
        <div style={statsGridStyles}>
          <div style={statCardStyles}>
            <div style={{ ...statValueStyles, color: accuracyColor }}>
              {summary.accuracy}%
            </div>
            <div style={statLabelStyles}>Accuracy</div>
          </div>

          <div style={statCardStyles}>
            <div style={statValueStyles}>{summary.questions_attempted}</div>
            <div style={statLabelStyles}>Questions</div>
          </div>

          <div style={statCardStyles}>
            <div style={{ ...statValueStyles, color: theme.colors.success[500] }}>
              {summary.questions_correct}
            </div>
            <div style={statLabelStyles}>Correct</div>
          </div>

          <div style={statCardStyles}>
            <div style={statValueStyles}>{formatTime(summary.total_time_ms)}</div>
            <div style={statLabelStyles}>Total Time</div>
          </div>

          <div style={statCardStyles}>
            <div style={statValueStyles}>{formatTime(summary.avg_time_per_question_ms)}</div>
            <div style={statLabelStyles}>Avg / Question</div>
          </div>
        </div>

        {summary.subjects_practiced.length > 0 && (
          <Card>
            <div style={{ marginBottom: theme.spacing[4] }}>
              <h3 style={theme.typography.styles.h3}>Subjects Practiced</h3>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: theme.spacing[2] }}>
              {summary.subjects_practiced.map((subject) => (
                <div
                  key={subject}
                  style={{
                    padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
                    backgroundColor: theme.colors.background.secondary,
                    borderRadius: theme.borderRadius.full,
                    fontSize: theme.typography.fontSize.sm,
                    fontWeight: theme.typography.fontWeight.medium,
                  }}
                >
                  {subject}
                </div>
              ))}
            </div>
          </Card>
        )}

        <div style={buttonGroupStyles}>
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
          <Button onClick={() => navigate('/dashboard')}>Practice Again</Button>
        </div>
      </div>
    </div>
  );
};
