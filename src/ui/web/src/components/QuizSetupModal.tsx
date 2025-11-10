/**
 * Quiz Setup Modal
 * Modal for configuring and creating a new quiz session
 */

import React, { useState, useEffect } from 'react';
import { Button } from './Button';
import { Card } from './Card';
import { ErrorMessage } from './ErrorMessage';
import { LoadingSpinner } from './LoadingSpinner';
import { useQuiz } from '../contexts/QuizContext';
import { useChildren } from '../contexts/ChildrenContext';
import { standardsService } from '../services';
import { theme } from '../../../../core/theme';
import type { Standard } from '../types/api';

interface QuizSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const QuizSetupModal: React.FC<QuizSetupModalProps> = ({ isOpen, onClose }) => {
  const { createQuiz, isLoading, error: quizError, clearError } = useQuiz();
  const { selectedChild } = useChildren();

  // Form state
  const [subject, setSubject] = useState('Mathematics');
  const [topic, setTopic] = useState('');
  const [subtopic, setSubtopic] = useState('');
  const [questionCount, setQuestionCount] = useState(10);
  const [durationMinutes, setDurationMinutes] = useState(15);
  const [easyPercent, setEasyPercent] = useState(30);
  const [mediumPercent, setMediumPercent] = useState(50);
  const [hardPercent, setHardPercent] = useState(20);

  // Standards data
  const [standards, setStandards] = useState<Standard[]>([]);
  const [isLoadingStandards, setIsLoadingStandards] = useState(false);
  const [standardsError, setStandardsError] = useState<string | null>(null);

  const subjects = ['Mathematics', 'English Language Arts', 'Science', 'Social Studies'];

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen && !isLoading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose, isLoading]);

  // Load standards when subject changes
  useEffect(() => {
    if (!selectedChild || !subject) return;

    const loadStandards = async () => {
      setIsLoadingStandards(true);
      setStandardsError(null);
      try {
        const data = await standardsService.list(subject, selectedChild.grade || undefined);
        setStandards(data || []); // Ensure it's always an array
        // Reset topic when standards change
        setTopic('');
        setSubtopic('');
      } catch (err) {
        console.error('[QuizSetupModal] Failed to load standards:', err);
        setStandardsError('Failed to load topics');
        setStandards([]); // Reset to empty array on error
      } finally {
        setIsLoadingStandards(false);
      }
    };

    loadStandards();
  }, [subject, selectedChild]);

  // Get unique topics from standards (with defensive check)
  const topics = Array.from(new Set((standards || []).map((s) => s.domain).filter(Boolean))) as string[];

  // Get subtopics for selected topic (with defensive check)
  const subtopics = Array.from(
    new Set(
      (standards || [])
        .filter((s) => s.domain === topic)
        .map((s) => s.sub_domain)
        .filter(Boolean)
    )
  ) as string[];

  // Validate difficulty mix sums to 100
  const totalPercent = easyPercent + mediumPercent + hardPercent;
  const isValidMix = totalPercent === 100;

  // Calculate recommended duration based on difficulty mix
  // Formula: Easy: 60s, Medium: 90s, Hard: 120s
  const calculateRecommendedDuration = (): number => {
    const easyCount = Math.round((questionCount * easyPercent) / 100);
    const mediumCount = Math.round((questionCount * mediumPercent) / 100);
    const hardCount = Math.round((questionCount * hardPercent) / 100);

    const durationSeconds = (easyCount * 60) + (mediumCount * 90) + (hardCount * 120);
    return Math.ceil(durationSeconds / 60); // Convert to minutes
  };

  const recommendedDuration = isValidMix ? calculateRecommendedDuration() : durationMinutes;

  const useRecommendedDuration = () => {
    setDurationMinutes(recommendedDuration);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedChild) {
      return;
    }

    if (!isValidMix) {
      return;
    }

    if (!topic) {
      return;
    }

    try {
      await createQuiz({
        child_id: selectedChild.id,
        subject,
        topic,
        subtopic: subtopic || null,
        question_count: questionCount,
        duration_sec: durationMinutes * 60,
        difficulty_mix: {
          easy: easyPercent / 100,
          medium: mediumPercent / 100,
          hard: hardPercent / 100,
        },
      });

      // Navigate to quiz page - quiz context will have the session
      // We'll need to get the session ID from the context after creation
      onClose();
    } catch (err) {
      console.error('[QuizSetupModal] Failed to create quiz:', err);
    }
  };

  const handleClose = () => {
    // Prevent closing during quiz creation
    if (isLoading) return;
    clearError();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      style={styles.overlay}
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="quiz-setup-title"
    >
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <Card style={styles.card}>
          <div style={styles.header}>
            <h2 id="quiz-setup-title" style={styles.title}>Create New Quiz</h2>
            <button onClick={handleClose} style={styles.closeButton} aria-label="Close">
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} style={styles.form}>
            {/* Subject Selector */}
            <div style={styles.formGroup}>
              <label htmlFor="subject" style={styles.label}>
                Subject
              </label>
              <select
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                style={styles.select}
                required
              >
                {subjects.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Topic Selector */}
            <div style={styles.formGroup}>
              <label htmlFor="topic" style={styles.label}>
                Topic
              </label>
              {isLoadingStandards ? (
                <p style={styles.loadingText}>Loading topics...</p>
              ) : standardsError ? (
                <ErrorMessage message={standardsError} />
              ) : topics.length > 0 ? (
                <select
                  id="topic"
                  value={topic}
                  onChange={(e) => {
                    setTopic(e.target.value);
                    setSubtopic('');
                  }}
                  style={styles.select}
                  required
                >
                  <option value="">Select a topic</option>
                  {topics.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              ) : (
                <p style={styles.noDataText}>No topics available for this subject and grade</p>
              )}
            </div>

            {/* Subtopic Selector (optional) */}
            {subtopics.length > 0 && (
              <div style={styles.formGroup}>
                <label htmlFor="subtopic" style={styles.label}>
                  Subtopic (Optional)
                </label>
                <select
                  id="subtopic"
                  value={subtopic}
                  onChange={(e) => setSubtopic(e.target.value)}
                  style={styles.select}
                >
                  <option value="">All subtopics</option>
                  {subtopics.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Question Count */}
            <div style={styles.formGroup}>
              <label htmlFor="questionCount" style={styles.label}>
                Number of Questions: {questionCount}
              </label>
              <input
                type="range"
                id="questionCount"
                min="5"
                max="30"
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
                style={styles.slider}
              />
              <div style={styles.sliderLabels}>
                <span>5</span>
                <span>30</span>
              </div>
            </div>

            {/* Duration */}
            <div style={styles.formGroup}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: theme.spacing[2],
              }}>
                <label htmlFor="duration" style={styles.label}>
                  Duration: {durationMinutes} minutes
                </label>
                {isValidMix && durationMinutes !== recommendedDuration && (
                  <button
                    type="button"
                    onClick={useRecommendedDuration}
                    style={styles.recommendButton}
                  >
                    Use Recommended ({recommendedDuration} min)
                  </button>
                )}
              </div>
              <input
                type="range"
                id="duration"
                min="5"
                max="120"
                step="5"
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                style={styles.slider}
              />
              <div style={styles.sliderLabels}>
                <span>5 min</span>
                <span>120 min</span>
              </div>
              {isValidMix && (
                <p style={styles.durationHint}>
                  Recommended: {recommendedDuration} min (based on {Math.round((questionCount * easyPercent) / 100)} easy @ 60s, {Math.round((questionCount * mediumPercent) / 100)} medium @ 90s, {Math.round((questionCount * hardPercent) / 100)} hard @ 120s)
                </p>
              )}
            </div>

            {/* Difficulty Mix */}
            <div style={styles.formGroup}>
              <label style={styles.label}>
                Difficulty Mix
                {!isValidMix && (
                  <span style={styles.errorLabel}> (must total 100%)</span>
                )}
              </label>

              <div style={styles.difficultyGrid}>
                <div style={styles.difficultyItem}>
                  <label htmlFor="easy" style={styles.difficultyLabel}>
                    Easy
                  </label>
                  <div style={styles.percentInput}>
                    <input
                      type="number"
                      id="easy"
                      min="0"
                      max="100"
                      value={easyPercent}
                      onChange={(e) => setEasyPercent(Number(e.target.value))}
                      style={styles.numberInput}
                    />
                    <span style={styles.percentSymbol}>%</span>
                  </div>
                </div>

                <div style={styles.difficultyItem}>
                  <label htmlFor="medium" style={styles.difficultyLabel}>
                    Medium
                  </label>
                  <div style={styles.percentInput}>
                    <input
                      type="number"
                      id="medium"
                      min="0"
                      max="100"
                      value={mediumPercent}
                      onChange={(e) => setMediumPercent(Number(e.target.value))}
                      style={styles.numberInput}
                    />
                    <span style={styles.percentSymbol}>%</span>
                  </div>
                </div>

                <div style={styles.difficultyItem}>
                  <label htmlFor="hard" style={styles.difficultyLabel}>
                    Hard
                  </label>
                  <div style={styles.percentInput}>
                    <input
                      type="number"
                      id="hard"
                      min="0"
                      max="100"
                      value={hardPercent}
                      onChange={(e) => setHardPercent(Number(e.target.value))}
                      style={styles.numberInput}
                    />
                    <span style={styles.percentSymbol}>%</span>
                  </div>
                </div>
              </div>

              <div style={styles.totalDisplay}>
                Total: <strong style={{ color: isValidMix ? theme.colors.success[600] : theme.colors.error[600] }}>
                  {totalPercent}%
                </strong>
              </div>
            </div>

            {/* Error Display */}
            {quizError && <ErrorMessage message={quizError} />}

            {/* Action Buttons */}
            <div style={styles.actions}>
              <Button type="button" variant="outline" onClick={handleClose} disabled={isLoading}>
                Cancel
              </Button>
              <Button
                type="submit"
                loading={isLoading}
                disabled={!topic || !isValidMix || isLoading}
              >
                Create Quiz
              </Button>
            </div>
          </form>
        </Card>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div style={styles.loadingOverlay}>
          <div style={styles.loadingContent}>
            <LoadingSpinner size="lg" />
            <p style={styles.overlayLoadingText}>Creating your quiz...</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  overlay: {
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
    overflowY: 'auto',
  },
  modal: {
    width: '100%',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflowY: 'auto',
  },
  card: {
    padding: 0,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing[6],
    borderBottom: `1px solid ${theme.colors.gray[200]}`,
  },
  title: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: theme.typography.fontSize['2xl'],
    color: theme.colors.text.secondary,
    cursor: 'pointer',
    padding: theme.spacing[2],
    lineHeight: '1',
    transition: theme.animations.transition.all,
  },
  form: {
    padding: theme.spacing[6],
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[5],
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
  },
  label: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },
  errorLabel: {
    color: theme.colors.error[600],
    fontWeight: theme.typography.fontWeight.normal,
  },
  select: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${theme.colors.gray[300]}`,
    backgroundColor: theme.colors.background.surface,
    color: theme.colors.text.primary,
    cursor: 'pointer',
    transition: theme.animations.transition.all,
  },
  slider: {
    width: '100%',
    height: '8px',
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.gray[200],
    cursor: 'pointer',
    accentColor: theme.colors.primary[500],
  },
  sliderLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.text.secondary,
  },
  difficultyGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: theme.spacing[3],
  },
  difficultyItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
  },
  difficultyLabel: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.secondary,
  },
  percentInput: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  numberInput: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    padding: `${theme.spacing[2]} ${theme.spacing[8]} ${theme.spacing[2]} ${theme.spacing[3]}`,
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${theme.colors.gray[300]}`,
    backgroundColor: theme.colors.background.surface,
    color: theme.colors.text.primary,
    width: '100%',
  },
  percentSymbol: {
    position: 'absolute',
    right: theme.spacing[3],
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  },
  totalDisplay: {
    textAlign: 'center',
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
    padding: theme.spacing[2],
  },
  loadingText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    fontStyle: 'italic',
  },
  noDataText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    fontStyle: 'italic',
  },
  recommendButton: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.medium,
    padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
    borderRadius: theme.borderRadius.md,
    border: `1px solid ${theme.colors.primary[300]}`,
    backgroundColor: theme.colors.primary[50],
    color: theme.colors.primary[700],
    cursor: 'pointer',
    transition: theme.animations.transition.all,
    whiteSpace: 'nowrap',
  },
  durationHint: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing[2],
    fontStyle: 'italic',
    lineHeight: theme.typography.lineHeight.relaxed,
  },
  actions: {
    display: 'flex',
    gap: theme.spacing[3],
    justifyContent: 'flex-end',
    paddingTop: theme.spacing[4],
    borderTop: `1px solid ${theme.colors.gray[200]}`,
  },
  loadingOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1002, // Above modal (1001)
  },
  loadingContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing[4],
  },
  overlayLoadingText: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: '#ffffff',
    margin: 0,
  },
};
