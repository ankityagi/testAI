/**
 * Practice Panel Component
 * Question practice session with subject/topic selection and answer submission
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { theme } from '../../../../../core/theme';
import { usePractice, useChildren } from '../../contexts';
import { Button, Toast } from '..';
import { questionsService } from '../../services';
import type { QuestionRequest } from '../../types/api';

export const PracticePanel: React.FC = () => {
  const navigate = useNavigate();
  const { selectedChild } = useChildren();
  const {
    currentQuestion,
    selectedSubtopic,
    sessionId,
    isLoading,
    error,
    fetchQuestions,
    selectAnswer,
    submitAnswer,
    nextQuestion,
    resetSession,
    endSession,
    questionsAnswered,
    correctAnswers,
    accuracy,
    clearError,
  } = usePractice();

  const [subject, setSubject] = useState('math');
  const [topic, setTopic] = useState('');
  const [subtopic, setSubtopic] = useState('');
  const [difficulty, setDifficulty] = useState('dynamic');
  const [showResult, setShowResult] = useState(false);
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(
    null
  );

  const handleStartSession = async (): Promise<void> => {
    if (!selectedChild) {
      setToast({ message: 'Please select a child first', variant: 'error' });
      return;
    }

    try {
      const request: QuestionRequest = {
        child_id: selectedChild.id,
        subject,
        topic: topic || null,
        subtopic: subtopic || null,
        limit: 5,
      };

      console.log('[PracticePanel] Starting session with request:', {
        child_id: selectedChild.id,
        child_name: selectedChild.name,
        subject,
        topic: topic || '(any)',
        subtopic: subtopic || '(any)',
        difficulty: difficulty === 'dynamic' ? '(adaptive)' : difficulty,
        limit: 5,
      });

      if (difficulty === 'dynamic') {
        console.log(
          '[PracticePanel] 🎯 Adaptive difficulty mode - backend will select difficulty based on child performance'
        );
      }

      await fetchQuestions(request);
      setShowResult(false);
    } catch {
      setToast({ message: 'Failed to load questions', variant: 'error' });
    }
  };

  const handleSubmitAnswer = async (): Promise<void> => {
    if (!currentQuestion?.selectedAnswer) {
      setToast({ message: 'Please select an answer', variant: 'error' });
      return;
    }

    if (!selectedChild) {
      setToast({ message: 'Please select a child', variant: 'error' });
      return;
    }

    try {
      const result = await submitAnswer(selectedChild.id);
      if (result) {
        setShowResult(true);
        if (result.correct) {
          setToast({ message: '✓ Correct!', variant: 'success' });
        } else {
          setToast({ message: '✗ Incorrect', variant: 'error' });
        }
      }
    } catch {
      setToast({ message: 'Failed to submit answer', variant: 'error' });
    }
  };

  const handleNextQuestion = (): void => {
    nextQuestion();
    setShowResult(false);
  };

  const handleEndSession = async (): Promise<void> => {
    console.log('[PracticePanel] handleEndSession called, sessionId:', sessionId);

    if (!sessionId) {
      console.warn('[PracticePanel] No sessionId available, resetting session without API call');
      resetSession();
      setShowResult(false);
      return;
    }

    try {
      console.log('[PracticePanel] Ending session:', sessionId);
      await endSession();
      console.log('[PracticePanel] Session ended successfully, navigating to summary');
      // Navigate to session summary
      navigate(`/session/${sessionId}/summary`);
    } catch (err) {
      console.error('[PracticePanel] Error ending session:', err);
      const errorMessage = (err as { detail?: string })?.detail || 'Failed to end session';
      setToast({ message: errorMessage, variant: 'error' });
    }
  };

  const handleResetSession = (): void => {
    resetSession();
    setShowResult(false);
  };

  // Styles
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const setupStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
  };

  const selectGroupStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
  };

  const labelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
  };

  const selectStyles: React.CSSProperties = {
    padding: theme.spacing[2],
    fontSize: theme.typography.fontSize.base,
    borderRadius: theme.borderRadius.sm,
    border: `1px solid ${theme.colors.border.light}`,
    backgroundColor: theme.colors.background.primary,
    outline: 'none',
    transition: theme.animations.transition.all,
  };

  const statsStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-around',
    padding: theme.spacing[3],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
  };

  const statItemStyles: React.CSSProperties = {
    textAlign: 'center',
  };

  const statValueStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.primary[500],
  };

  const statLabelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  };

  const questionCardStyles: React.CSSProperties = {
    padding: theme.spacing[6],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.lg,
    border: `1px solid ${theme.colors.border.light}`,
  };

  const questionTextStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.medium,
    marginBottom: theme.spacing[6],
    lineHeight: 1.6,
  };

  const choicesStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  };

  const choiceButtonStyles = (
    choice: string,
    isSelected: boolean,
    isAnswered: boolean,
    isCorrect: boolean | null
  ): React.CSSProperties => {
    let backgroundColor: string = theme.colors.background.primary;
    let borderColor: string = theme.colors.border.light;
    let color: string = theme.colors.text.primary;

    if (isSelected && !isAnswered) {
      backgroundColor = theme.colors.primary[50];
      borderColor = theme.colors.primary[500];
      color = theme.colors.primary[700];
    }

    if (isAnswered) {
      if (choice === currentQuestion?.question.correct_answer) {
        backgroundColor = theme.colors.success[50];
        borderColor = theme.colors.success[500];
        color = theme.colors.success[700];
      } else if (isSelected && !isCorrect) {
        backgroundColor = theme.colors.error[50];
        borderColor = theme.colors.error[500];
        color = theme.colors.error[700];
      }
    }

    return {
      padding: theme.spacing[4],
      textAlign: 'left',
      fontSize: theme.typography.fontSize.base,
      borderRadius: theme.borderRadius.md,
      border: `2px solid ${borderColor}`,
      backgroundColor,
      color,
      cursor: isAnswered ? 'default' : 'pointer',
      transition: theme.animations.transition.all,
      fontWeight: isSelected
        ? theme.typography.fontWeight.medium
        : theme.typography.fontWeight.normal,
    };
  };

  const actionButtonsStyles: React.CSSProperties = {
    display: 'flex',
    gap: theme.spacing[3],
    marginTop: theme.spacing[4],
  };

  const subtopicBadgeStyles: React.CSSProperties = {
    display: 'inline-block',
    padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
    backgroundColor: theme.colors.primary[100],
    color: theme.colors.primary[700],
    borderRadius: theme.borderRadius.full,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    marginBottom: theme.spacing[4],
  };

  const completionStyles: React.CSSProperties = {
    textAlign: 'center',
    padding: theme.spacing[8],
  };

  const completionIconStyles: React.CSSProperties = {
    fontSize: '64px',
    marginBottom: theme.spacing[4],
  };

  // Render setup form
  if (!currentQuestion) {
    return (
      <div style={containerStyles}>
        {questionsAnswered > 0 ? (
          // Session completed
          <div style={completionStyles}>
            <div style={completionIconStyles}>🎉</div>
            <h3 style={theme.typography.styles.h3}>Session Complete!</h3>
            <p style={{ color: theme.colors.text.secondary, marginBottom: theme.spacing[4] }}>
              You answered {questionsAnswered} questions with {accuracy}% accuracy
            </p>
            <div style={{ display: 'flex', gap: theme.spacing[3], justifyContent: 'center' }}>
              <Button variant="secondary" onClick={handleResetSession}>
                Start New Session
              </Button>
              {sessionId && (
                <Button variant="primary" onClick={handleEndSession}>
                  View Summary
                </Button>
              )}
            </div>
          </div>
        ) : (
          // Setup form
          <>
            <div style={setupStyles}>
              <h4 style={theme.typography.styles.h4}>Practice Setup</h4>

              <div style={selectGroupStyles}>
                <label style={labelStyles}>Subject</label>
                <select
                  style={selectStyles}
                  value={subject}
                  onChange={(e) => {
                    setSubject(e.target.value);
                    setTopic(''); // Reset topic when subject changes
                  }}
                  disabled={isLoading}
                >
                  {questionsService.getSubjects().map((s) => (
                    <option key={s} value={s}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div style={selectGroupStyles}>
                <label style={labelStyles}>Topic (Optional)</label>
                <select
                  style={selectStyles}
                  value={topic}
                  onChange={(e) => {
                    setTopic(e.target.value);
                    setSubtopic(''); // Reset subtopic when topic changes
                  }}
                  disabled={isLoading}
                >
                  <option value="">Any Topic</option>
                  {questionsService.getTopics(subject).map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div style={selectGroupStyles}>
                <label style={labelStyles}>Subtopic (Optional)</label>
                <select
                  style={selectStyles}
                  value={subtopic}
                  onChange={(e) => setSubtopic(e.target.value)}
                  disabled={isLoading || !topic}
                >
                  <option value="">Any Subtopic</option>
                  {topic &&
                    questionsService.getSubtopics(subject, topic).map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                </select>
              </div>

              <div style={selectGroupStyles}>
                <label style={labelStyles}>Difficulty</label>
                <select
                  style={selectStyles}
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  disabled={isLoading}
                >
                  {questionsService.getDifficultyLevels().map((d) => (
                    <option key={d} value={d}>
                      {d === 'dynamic'
                        ? '🎯 Adaptive (Recommended)'
                        : d.charAt(0).toUpperCase() + d.slice(1)}
                    </option>
                  ))}
                </select>
                {difficulty === 'dynamic' && (
                  <p
                    style={{
                      fontSize: theme.typography.fontSize.xs,
                      color: theme.colors.text.secondary,
                      marginTop: theme.spacing[1],
                    }}
                  >
                    Difficulty adjusts based on performance history and streaks
                  </p>
                )}
              </div>

              <Button
                variant="primary"
                fullWidth
                onClick={handleStartSession}
                loading={isLoading}
                disabled={isLoading || !selectedChild}
              >
                Start Practice
              </Button>

              {!selectedChild && (
                <p
                  style={{
                    fontSize: theme.typography.fontSize.sm,
                    color: theme.colors.text.secondary,
                    textAlign: 'center',
                  }}
                >
                  Please select a child from the Children panel to start practicing
                </p>
              )}
            </div>
          </>
        )}

        {error && <Toast message={error} variant="error" onDismiss={clearError} />}

        {toast && (
          <Toast message={toast.message} variant={toast.variant} onDismiss={() => setToast(null)} />
        )}
      </div>
    );
  }

  // Render question
  return (
    <div style={containerStyles}>
      {/* Session stats */}
      <div style={statsStyles}>
        <div style={statItemStyles}>
          <div style={statValueStyles}>{questionsAnswered}</div>
          <div style={statLabelStyles}>Answered</div>
        </div>
        <div style={statItemStyles}>
          <div style={statValueStyles}>{correctAnswers}</div>
          <div style={statLabelStyles}>Correct</div>
        </div>
        <div style={statItemStyles}>
          <div style={statValueStyles}>{accuracy}%</div>
          <div style={statLabelStyles}>Accuracy</div>
        </div>
      </div>

      {/* Question card */}
      <div style={questionCardStyles}>
        {selectedSubtopic && <div style={subtopicBadgeStyles}>{selectedSubtopic}</div>}

        <div style={questionTextStyles}>{currentQuestion.question.stem}</div>

        <div style={choicesStyles}>
          {currentQuestion.question.options.map((choice: string) => (
            <button
              key={choice}
              style={choiceButtonStyles(
                choice,
                currentQuestion.selectedAnswer === choice,
                currentQuestion.isAnswered,
                currentQuestion.isCorrect
              )}
              onClick={() => !currentQuestion.isAnswered && selectAnswer(choice)}
              disabled={currentQuestion.isAnswered}
              onMouseEnter={(e) => {
                if (!currentQuestion.isAnswered && currentQuestion.selectedAnswer !== choice) {
                  e.currentTarget.style.borderColor = theme.colors.primary[300];
                  e.currentTarget.style.transform = 'translateX(4px)';
                }
              }}
              onMouseLeave={(e) => {
                if (!currentQuestion.isAnswered && currentQuestion.selectedAnswer !== choice) {
                  e.currentTarget.style.borderColor = theme.colors.border.light;
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              {choice}
            </button>
          ))}
        </div>

        <div style={actionButtonsStyles}>
          {!showResult ? (
            <Button
              variant="primary"
              fullWidth
              onClick={handleSubmitAnswer}
              disabled={!currentQuestion.selectedAnswer || isLoading}
              loading={isLoading}
            >
              Submit Answer
            </Button>
          ) : (
            <>
              <Button variant="primary" fullWidth onClick={handleNextQuestion}>
                Next Question
              </Button>
              <Button variant="ghost" onClick={handleEndSession}>
                End Session
              </Button>
            </>
          )}
        </div>

        {showResult && currentQuestion.isAnswered && (
          <div
            style={{
              marginTop: theme.spacing[4],
              padding: theme.spacing[4],
              backgroundColor: currentQuestion.isCorrect
                ? theme.colors.success[50]
                : theme.colors.error[50],
              borderRadius: theme.borderRadius.md,
              border: `1px solid ${
                currentQuestion.isCorrect ? theme.colors.success[200] : theme.colors.error[200]
              }`,
            }}
          >
            <div
              style={{
                fontWeight: theme.typography.fontWeight.medium,
                marginBottom: theme.spacing[2],
              }}
            >
              {currentQuestion.isCorrect ? '✓ Correct!' : '✗ Incorrect'}
            </div>
            {currentQuestion.question.rationale && (
              <div
                style={{
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.text.secondary,
                }}
              >
                {currentQuestion.question.rationale}
              </div>
            )}
          </div>
        )}
      </div>

      {error && <Toast message={error} variant="error" onDismiss={clearError} />}

      {toast && (
        <Toast message={toast.message} variant={toast.variant} onDismiss={() => setToast(null)} />
      )}
    </div>
  );
};
