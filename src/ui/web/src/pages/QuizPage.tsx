/**
 * Quiz Page
 * Main quiz interface with timer, questions, and submission
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuiz } from '../contexts/QuizContext';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { theme } from '../../../../core/theme';

export const QuizPage: React.FC = () => {
  const { id: sessionId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    session,
    questions,
    answers,
    timeRemaining,
    isLoading,
    isSubmitting,
    error,
    loadQuiz,
    selectAnswer,
    submitQuiz,
    isExpired,
    percentTimeRemaining,
  } = useQuiz();

  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const questionRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Load quiz on mount
  useEffect(() => {
    if (sessionId && !session) {
      loadQuiz(sessionId).catch((err) => {
        console.error('[QuizPage] Failed to load quiz:', err);
      });
    }
  }, [sessionId, session, loadQuiz]);

  // Redirect to results if already completed
  useEffect(() => {
    if (session?.status === 'completed') {
      navigate(`/quiz/${session.id}/results`, { replace: true });
    }
  }, [session, navigate]);

  const handleSubmit = async () => {
    const unansweredCount = questions.length - Object.keys(answers).length;

    if (unansweredCount > 0 && !isExpired) {
      setShowSubmitConfirm(true);
      return;
    }

    await submitQuiz();
    if (session) {
      navigate(`/quiz/${session.id}/results`);
    }
  };

  const handleConfirmedSubmit = async () => {
    setShowSubmitConfirm(false);
    await submitQuiz();
    if (session) {
      navigate(`/quiz/${session.id}/results`);
    }
  };

  const scrollToQuestion = (index: number) => {
    questionRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = (): string => {
    if (percentTimeRemaining > 50) return theme.colors.success[500];
    if (percentTimeRemaining > 25) return theme.colors.warning[500];
    return theme.colors.error[500];
  };

  if (isLoading) {
    return (
      <div style={styles.loadingContainer}>
        <LoadingSpinner size="lg" />
        <p style={styles.loadingText}>Loading quiz...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <ErrorMessage message={error} />
        <Button onClick={() => navigate('/dashboard')} style={{ marginTop: theme.spacing[4] }}>
          Return to Dashboard
        </Button>
      </div>
    );
  }

  if (!session || !questions.length) {
    return (
      <div style={styles.errorContainer}>
        <ErrorMessage message="Quiz session not found" />
        <Button onClick={() => navigate('/dashboard')} style={{ marginTop: theme.spacing[4] }}>
          Return to Dashboard
        </Button>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const totalQuestions = questions.length;
  const showQuestionNav = totalQuestions >= 10;

  return (
    <div style={styles.pageContainer}>
      {/* Sticky Timer Bar */}
      <div style={styles.timerBar}>
        <div style={styles.timerContent}>
          <div style={styles.timerInfo}>
            <h2 style={styles.timerTitle}>
              {session.subject} - {session.topic}
              {session.subtopic && ` - ${session.subtopic}`}
            </h2>
            <p style={styles.progressText}>
              {answeredCount} of {totalQuestions} answered
            </p>
          </div>

          <div style={styles.timerDisplay}>
            <div style={{...styles.timeText, color: getTimerColor()}}>
              {timeRemaining !== null ? formatTime(timeRemaining) : '--:--'}
            </div>
            <div
              style={styles.progressBarContainer}
              role="progressbar"
              aria-label="Time remaining"
              aria-valuenow={percentTimeRemaining}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                style={{
                  ...styles.progressBarFill,
                  width: `${percentTimeRemaining}%`,
                  backgroundColor: getTimerColor(),
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Question Navigation (for 10+ questions) */}
      {showQuestionNav && (
        <div style={styles.questionNav}>
          <p style={styles.questionNavLabel}>Jump to:</p>
          <div style={styles.questionNavButtons}>
            {questions.map((q, idx) => (
              <button
                key={q.id}
                onClick={() => scrollToQuestion(idx)}
                style={{
                  ...styles.navButton,
                  ...(answers[q.id] ? styles.navButtonAnswered : {}),
                }}
              >
                {idx + 1}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Questions List */}
      <div style={styles.questionsContainer}>
        {questions.map((question, idx) => (
          <div
            key={question.id}
            ref={(el) => (questionRefs.current[idx] = el)}
            style={styles.questionCard}
          >
            <Card>
              <div style={styles.questionHeader}>
                <span style={styles.questionNumber}>Question {idx + 1}</span>
                {question.difficulty && (
                  <span style={{
                    ...styles.difficultyBadge,
                    backgroundColor: getDifficultyColor(question.difficulty),
                  }}>
                    {question.difficulty}
                  </span>
                )}
              </div>

              <p style={styles.questionStem}>{question.stem}</p>

              <div style={styles.optionsContainer}>
                {question.options.map((option, optionIdx) => {
                  const optionId = `q${question.id}-opt${optionIdx}`;
                  const isSelected = answers[question.id] === option;

                  return (
                    <label
                      key={optionIdx}
                      htmlFor={optionId}
                      style={{
                        ...styles.optionLabel,
                        ...(isSelected ? styles.optionLabelSelected : {}),
                      }}
                    >
                      <input
                        type="radio"
                        id={optionId}
                        name={`question-${question.id}`}
                        value={option}
                        checked={isSelected}
                        onChange={() => selectAnswer(question.id, option)}
                        style={styles.radioInput}
                      />
                      <span style={styles.optionText}>{option}</span>
                    </label>
                  );
                })}
              </div>
            </Card>
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <div style={styles.submitContainer}>
        <Button
          onClick={handleSubmit}
          loading={isSubmitting}
          disabled={isSubmitting || answeredCount === 0}
          size="lg"
          fullWidth
        >
          {isExpired ? 'Time Expired - Submit Quiz' : 'Submit Quiz'}
        </Button>
      </div>

      {/* Submit Confirmation Modal */}
      {showSubmitConfirm && (
        <div style={styles.modalOverlay} onClick={() => setShowSubmitConfirm(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3 style={styles.modalTitle}>Submit Quiz?</h3>
            <p style={styles.modalText}>
              You have {totalQuestions - answeredCount} unanswered question
              {totalQuestions - answeredCount !== 1 ? 's' : ''}.
              Are you sure you want to submit?
            </p>
            <div style={styles.modalButtons}>
              <Button variant="outline" onClick={() => setShowSubmitConfirm(false)}>
                Continue Quiz
              </Button>
              <Button onClick={handleConfirmedSubmit} loading={isSubmitting}>
                Submit Anyway
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function
const getDifficultyColor = (difficulty: string): string => {
  switch (difficulty.toLowerCase()) {
    case 'easy':
      return theme.colors.success[100];
    case 'medium':
      return theme.colors.warning[100];
    case 'hard':
      return theme.colors.error[100];
    default:
      return theme.colors.gray[100];
  }
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  pageContainer: {
    minHeight: '100vh',
    backgroundColor: theme.colors.background.page,
    paddingBottom: theme.spacing[20],
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
  timerBar: {
    position: 'sticky',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.background.surface,
    borderBottom: `1px solid ${theme.colors.gray[200]}`,
    boxShadow: theme.shadows.md,
    zIndex: 100,
    padding: `${theme.spacing[4]} ${theme.spacing[6]}`,
  },
  timerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: theme.spacing[6],
    flexWrap: 'wrap',
  },
  timerInfo: {
    flex: '1 1 300px',
  },
  timerTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
    marginBottom: theme.spacing[1],
  },
  progressText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    margin: 0,
  },
  timerDisplay: {
    flex: '0 0 auto',
    textAlign: 'right',
  },
  timeText: {
    fontFamily: theme.typography.fonts.mono,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    marginBottom: theme.spacing[2],
  },
  progressBarContainer: {
    width: '200px',
    height: '8px',
    backgroundColor: theme.colors.gray[200],
    borderRadius: theme.borderRadius.full,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    transition: 'width 1s linear, background-color 0.3s ease',
    borderRadius: theme.borderRadius.full,
  },
  questionNav: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: theme.spacing[4],
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[4],
    flexWrap: 'wrap',
  },
  questionNavLabel: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.secondary,
    margin: 0,
  },
  questionNavButtons: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: theme.spacing[2],
  },
  navButton: {
    width: '44px',
    height: '44px',
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${theme.colors.gray[300]}`,
    backgroundColor: theme.colors.background.surface,
    color: theme.colors.text.primary,
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    cursor: 'pointer',
    transition: theme.animations.transition.all,
  },
  navButtonAnswered: {
    backgroundColor: theme.colors.primary[500],
    borderColor: theme.colors.primary[500],
    color: theme.colors.text.inverse,
  },
  questionsContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: theme.spacing[6],
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[6],
  },
  questionCard: {
    width: '100%',
  },
  questionHeader: {
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
    letterSpacing: '0.05em',
  },
  difficultyBadge: {
    padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
    borderRadius: theme.borderRadius.full,
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.semibold,
    textTransform: 'capitalize',
  },
  questionStem: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
    lineHeight: theme.typography.lineHeight.relaxed,
    marginBottom: theme.spacing[4],
  },
  optionsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  },
  optionLabel: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: theme.spacing[3],
    padding: theme.spacing[4],
    borderRadius: theme.borderRadius.lg,
    border: `2px solid ${theme.colors.gray[200]}`,
    backgroundColor: theme.colors.background.surface,
    cursor: 'pointer',
    transition: theme.animations.transition.all,
    minHeight: '44px',
  },
  optionLabelSelected: {
    borderColor: theme.colors.primary[500],
    backgroundColor: theme.colors.primary[50],
    boxShadow: theme.shadows.sm,
  },
  radioInput: {
    width: '20px',
    height: '20px',
    marginTop: '2px',
    cursor: 'pointer',
    accentColor: theme.colors.primary[500],
  },
  optionText: {
    flex: 1,
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
    lineHeight: theme.typography.lineHeight.normal,
  },
  submitContainer: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.background.surface,
    borderTop: `1px solid ${theme.colors.gray[200]}`,
    padding: theme.spacing[4],
    boxShadow: theme.shadows.lg,
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: theme.spacing[4],
  },
  modalContent: {
    backgroundColor: theme.colors.background.surface,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing[6],
    maxWidth: '500px',
    width: '100%',
    boxShadow: theme.shadows.xl,
  },
  modalTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
    marginBottom: theme.spacing[3],
  },
  modalText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
    lineHeight: theme.typography.lineHeight.relaxed,
    marginBottom: theme.spacing[6],
  },
  modalButtons: {
    display: 'flex',
    gap: theme.spacing[3],
    justifyContent: 'flex-end',
  },
};
