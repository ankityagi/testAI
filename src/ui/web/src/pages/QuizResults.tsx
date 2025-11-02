/**
 * Quiz Results Page
 * Displays quiz score, time taken, and detailed feedback on incorrect answers
 */

import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuiz } from '../contexts/QuizContext';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { theme } from '../../../../core/theme';

export const QuizResults: React.FC = () => {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { session, result, isLoading, error, loadQuiz, resetQuiz } = useQuiz();

  // Load quiz on mount if not already loaded
  useEffect(() => {
    if (sessionId && !session) {
      loadQuiz(sessionId).catch((err) => {
        console.error('[QuizResults] Failed to load quiz:', err);
      });
    }
  }, [sessionId, session, loadQuiz]);

  // Redirect if quiz not completed
  useEffect(() => {
    if (session && session.status !== 'completed') {
      navigate(`/quiz/${session.id}`, { replace: true });
    }
  }, [session, navigate]);

  const handleNewQuiz = () => {
    resetQuiz();
    navigate('/dashboard');
  };

  const handleDashboard = () => {
    resetQuiz();
    navigate('/dashboard');
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins} min ${secs} sec`;
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return theme.colors.success[500];
    if (score >= 70) return theme.colors.warning[500];
    return theme.colors.error[500];
  };

  const getGrade = (score: number): string => {
    if (score >= 93) return 'A';
    if (score >= 90) return 'A-';
    if (score >= 87) return 'B+';
    if (score >= 83) return 'B';
    if (score >= 80) return 'B-';
    if (score >= 77) return 'C+';
    if (score >= 73) return 'C';
    if (score >= 70) return 'C-';
    if (score >= 67) return 'D+';
    if (score >= 60) return 'D';
    return 'F';
  };

  if (isLoading) {
    return (
      <div style={styles.loadingContainer}>
        <LoadingSpinner size="lg" />
        <p style={styles.loadingText}>Loading results...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <ErrorMessage message={error} />
        <Button onClick={handleDashboard} style={{ marginTop: theme.spacing[4] }}>
          Return to Dashboard
        </Button>
      </div>
    );
  }

  if (!session || !result) {
    return (
      <div style={styles.errorContainer}>
        <ErrorMessage message="Quiz results not found" />
        <Button onClick={handleDashboard} style={{ marginTop: theme.spacing[4] }}>
          Return to Dashboard
        </Button>
      </div>
    );
  }

  const scoreColor = getScoreColor(result.score);
  const grade = getGrade(result.score);
  const accuracy = (result.correct_count / result.total_questions) * 100;

  return (
    <div style={styles.pageContainer}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.pageTitle}>Quiz Complete!</h1>
        <p style={styles.quizInfo}>
          {session.subject} - {session.topic}
          {session.subtopic && ` - ${session.subtopic}`}
        </p>
      </div>

      <div style={styles.contentContainer}>
        {/* Score Card */}
        <Card style={styles.scoreCard}>
          <div style={styles.scoreHeader}>
            <div style={styles.gradeCircle}>
              <span style={{ ...styles.gradeText, color: scoreColor }}>{grade}</span>
            </div>
            <div style={styles.scoreDetails}>
              <div style={{ ...styles.scoreValue, color: scoreColor }}>
                {result.score}%
              </div>
              <p style={styles.scoreLabel}>Your Score</p>
            </div>
          </div>

          <div style={styles.statsGrid}>
            <div style={styles.statItem}>
              <span style={styles.statValue}>{result.correct_count}</span>
              <span style={styles.statLabel}>Correct</span>
            </div>
            <div style={styles.statItem}>
              <span style={styles.statValue}>
                {result.total_questions - result.correct_count}
              </span>
              <span style={styles.statLabel}>Incorrect</span>
            </div>
            <div style={styles.statItem}>
              <span style={styles.statValue}>{result.total_questions}</span>
              <span style={styles.statLabel}>Total</span>
            </div>
            <div style={styles.statItem}>
              <span style={styles.statValue}>{formatTime(result.time_taken_sec)}</span>
              <span style={styles.statLabel}>Time Taken</span>
            </div>
          </div>

          {/* Performance Message */}
          <div style={styles.performanceMessage}>
            {accuracy >= 90 ? (
              <p style={styles.excellentMessage}>
                Excellent work! You've mastered this topic.
              </p>
            ) : accuracy >= 70 ? (
              <p style={styles.goodMessage}>
                Good job! Keep practicing to improve further.
              </p>
            ) : (
              <p style={styles.needsWorkMessage}>
                Keep practicing! Review the explanations below to improve.
              </p>
            )}
          </div>
        </Card>

        {/* Incorrect Items */}
        {result.incorrect_items.length > 0 && (
          <div style={styles.incorrectSection}>
            <h2 style={styles.sectionTitle}>
              Review Incorrect Answers ({result.incorrect_items.length})
            </h2>
            <p style={styles.sectionDescription}>
              Study these explanations to understand where you can improve.
            </p>

            <div style={styles.incorrectList}>
              {result.incorrect_items.map((item) => (
                <Card key={item.question_id} style={styles.incorrectCard}>
                  <div style={styles.incorrectHeader}>
                    <span style={styles.questionNumber}>Question {item.index + 1}</span>
                    <span style={styles.incorrectBadge}>Incorrect</span>
                  </div>

                  <p style={styles.questionStem}>{item.stem}</p>

                  <div style={styles.answersContainer}>
                    {/* Your Answer */}
                    <div style={styles.answerBlock}>
                      <span style={styles.answerLabel}>Your Answer:</span>
                      <div style={{...styles.answerBox, ...styles.incorrectAnswer}}>
                        {item.selected_choice || '(No answer selected)'}
                      </div>
                    </div>

                    {/* Correct Answer */}
                    <div style={styles.answerBlock}>
                      <span style={styles.answerLabel}>Correct Answer:</span>
                      <div style={{...styles.answerBox, ...styles.correctAnswer}}>
                        {item.correct_choice}
                      </div>
                    </div>
                  </div>

                  {/* Explanation */}
                  <div style={styles.explanationContainer}>
                    <span style={styles.explanationLabel}>Explanation:</span>
                    <p style={styles.explanationText}>{item.explanation}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Perfect Score Message */}
        {result.incorrect_items.length === 0 && (
          <Card style={styles.perfectScoreCard}>
            <div style={styles.perfectScoreContent}>
              <span style={styles.perfectScoreEmoji}>🎉</span>
              <h3 style={styles.perfectScoreTitle}>Perfect Score!</h3>
              <p style={styles.perfectScoreText}>
                You answered all questions correctly. Outstanding work!
              </p>
            </div>
          </Card>
        )}

        {/* Action Buttons */}
        <div style={styles.actionsContainer}>
          <Button variant="outline" onClick={handleDashboard} size="lg">
            Return to Dashboard
          </Button>
          <Button onClick={handleNewQuiz} size="lg">
            Start New Quiz
          </Button>
        </div>
      </div>
    </div>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  pageContainer: {
    minHeight: '100vh',
    backgroundColor: theme.colors.background.page,
    paddingBottom: theme.spacing[8],
  },
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    gap: theme.spacing[4],
  },
  loadingText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
  },
  errorContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    padding: theme.spacing[4],
  },
  header: {
    backgroundColor: theme.colors.background.surface,
    borderBottom: `1px solid ${theme.colors.gray[200]}`,
    padding: `${theme.spacing[8]} ${theme.spacing[6]}`,
    textAlign: 'center',
  },
  pageTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
    marginBottom: theme.spacing[2],
  },
  quizInfo: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
    margin: 0,
  },
  contentContainer: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: theme.spacing[6],
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[6],
  },
  scoreCard: {
    padding: theme.spacing[8],
  },
  scoreHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[6],
    marginBottom: theme.spacing[6],
    justifyContent: 'center',
  },
  gradeCircle: {
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    backgroundColor: theme.colors.gray[100],
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: theme.shadows.lg,
  },
  gradeText: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: '56px',
    fontWeight: theme.typography.fontWeight.bold,
  },
  scoreDetails: {
    textAlign: 'left',
  },
  scoreValue: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: '72px',
    fontWeight: theme.typography.fontWeight.bold,
    lineHeight: '1',
    display: 'block',
  },
  scoreLabel: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
    margin: 0,
    marginTop: theme.spacing[2],
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: theme.spacing[4],
    marginBottom: theme.spacing[6],
  },
  statItem: {
    textAlign: 'center',
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.page,
    borderRadius: theme.borderRadius.lg,
  },
  statValue: {
    display: 'block',
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing[1],
  },
  statLabel: {
    display: 'block',
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  },
  performanceMessage: {
    textAlign: 'center',
    padding: theme.spacing[4],
    borderRadius: theme.borderRadius.lg,
    backgroundColor: theme.colors.background.page,
  },
  excellentMessage: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.success[700],
    margin: 0,
  },
  goodMessage: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.warning[700],
    margin: 0,
  },
  needsWorkMessage: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.error[700],
    margin: 0,
  },
  incorrectSection: {
    marginTop: theme.spacing[4],
  },
  sectionTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
    marginBottom: theme.spacing[2],
  },
  sectionDescription: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing[4],
  },
  incorrectList: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  },
  incorrectCard: {
    padding: theme.spacing[6],
  },
  incorrectHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing[3],
  },
  questionNumber: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.primary[600],
    textTransform: 'uppercase',
  },
  incorrectBadge: {
    padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.error[100],
    color: theme.colors.error[700],
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  questionStem: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
    lineHeight: theme.typography.lineHeight.relaxed,
    marginBottom: theme.spacing[4],
  },
  answersContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: theme.spacing[4],
    marginBottom: theme.spacing[4],
  },
  answerBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
  },
  answerLabel: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.secondary,
  },
  answerBox: {
    padding: theme.spacing[3],
    borderRadius: theme.borderRadius.md,
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    lineHeight: theme.typography.lineHeight.normal,
  },
  incorrectAnswer: {
    backgroundColor: theme.colors.error[50],
    border: `2px solid ${theme.colors.error[300]}`,
    color: theme.colors.error[900],
  },
  correctAnswer: {
    backgroundColor: theme.colors.success[50],
    border: `2px solid ${theme.colors.success[300]}`,
    color: theme.colors.success[900],
  },
  explanationContainer: {
    padding: theme.spacing[4],
    backgroundColor: theme.colors.primary[50],
    borderRadius: theme.borderRadius.lg,
    borderLeft: `4px solid ${theme.colors.primary[500]}`,
  },
  explanationLabel: {
    display: 'block',
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.primary[700],
    marginBottom: theme.spacing[2],
  },
  explanationText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
    lineHeight: theme.typography.lineHeight.relaxed,
    margin: 0,
  },
  perfectScoreCard: {
    padding: theme.spacing[8],
  },
  perfectScoreContent: {
    textAlign: 'center',
  },
  perfectScoreEmoji: {
    fontSize: '64px',
    display: 'block',
    marginBottom: theme.spacing[4],
  },
  perfectScoreTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.success[700],
    margin: 0,
    marginBottom: theme.spacing[2],
  },
  perfectScoreText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.text.secondary,
    margin: 0,
  },
  actionsContainer: {
    display: 'flex',
    gap: theme.spacing[4],
    justifyContent: 'center',
    flexWrap: 'wrap',
    marginTop: theme.spacing[4],
  },
};
