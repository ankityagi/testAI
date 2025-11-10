/**
 * Quiz Feedback Modal
 * Collects user feedback after quiz completion for progressive rollout monitoring
 */

import React, { useState } from 'react';
import { theme } from '../../../../core/theme';
import { Button } from './Button';

export interface QuizFeedback {
  session_id: string;
  duration_appropriate: 'too_short' | 'just_right' | 'too_long';
  questions_fair: 'too_easy' | 'appropriate' | 'too_hard';
  overall_rating: 1 | 2 | 3 | 4 | 5;
  comments?: string;
}

interface QuizFeedbackModalProps {
  isOpen: boolean;
  sessionId: string;
  onClose: () => void;
  onSubmit: (feedback: Omit<QuizFeedback, 'session_id'>) => Promise<void>;
}

export const QuizFeedbackModal: React.FC<QuizFeedbackModalProps> = ({
  isOpen,
  sessionId,
  onClose,
  onSubmit,
}) => {
  const [durationRating, setDurationRating] = useState<QuizFeedback['duration_appropriate']>('just_right');
  const [fairnessRating, setFairnessRating] = useState<QuizFeedback['questions_fair']>('appropriate');
  const [overallRating, setOverallRating] = useState<QuizFeedback['overall_rating']>(4);
  const [comments, setComments] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        duration_appropriate: durationRating,
        questions_fair: fairnessRating,
        overall_rating: overallRating,
        comments: comments.trim() || undefined,
      });
      onClose();
    } catch (error) {
      console.error('[QuizFeedbackModal] Failed to submit feedback:', error);
      // Still close on error to avoid blocking user
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div style={styles.backdrop} onClick={handleSkip} />

      {/* Modal */}
      <div style={styles.modal}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>How was your quiz?</h2>
          <p style={styles.modalSubtitle}>
            Help us improve by sharing your feedback
          </p>
        </div>

        <div style={styles.modalBody}>
          {/* Duration Rating */}
          <div style={styles.questionGroup}>
            <label style={styles.questionLabel}>Was the duration appropriate?</label>
            <div style={styles.optionsRow}>
              {(['too_short', 'just_right', 'too_long'] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  style={{
                    ...styles.optionButton,
                    ...(durationRating === option ? styles.optionButtonSelected : {}),
                  }}
                  onClick={() => setDurationRating(option)}
                >
                  {option === 'too_short' && 'Too Short'}
                  {option === 'just_right' && 'Just Right'}
                  {option === 'too_long' && 'Too Long'}
                </button>
              ))}
            </div>
          </div>

          {/* Fairness Rating */}
          <div style={styles.questionGroup}>
            <label style={styles.questionLabel}>Were the questions fair?</label>
            <div style={styles.optionsRow}>
              {(['too_easy', 'appropriate', 'too_hard'] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  style={{
                    ...styles.optionButton,
                    ...(fairnessRating === option ? styles.optionButtonSelected : {}),
                  }}
                  onClick={() => setFairnessRating(option)}
                >
                  {option === 'too_easy' && 'Too Easy'}
                  {option === 'appropriate' && 'Appropriate'}
                  {option === 'too_hard' && 'Too Hard'}
                </button>
              ))}
            </div>
          </div>

          {/* Overall Rating */}
          <div style={styles.questionGroup}>
            <label style={styles.questionLabel}>Overall rating</label>
            <div style={styles.starsRow}>
              {([1, 2, 3, 4, 5] as const).map((star) => (
                <button
                  key={star}
                  type="button"
                  style={styles.starButton}
                  onClick={() => setOverallRating(star)}
                  aria-label={`Rate ${star} stars`}
                >
                  <span style={{
                    ...styles.starIcon,
                    color: star <= overallRating ? theme.colors.warning[500] : theme.colors.gray[300],
                  }}>
                    ★
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Comments */}
          <div style={styles.questionGroup}>
            <label style={styles.questionLabel}>Additional comments (optional)</label>
            <textarea
              style={styles.textarea}
              placeholder="Tell us more about your experience..."
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={3}
              maxLength={500}
            />
            <span style={styles.charCount}>{comments.length}/500</span>
          </div>
        </div>

        <div style={styles.modalFooter}>
          <Button
            variant="ghost"
            onClick={handleSkip}
            disabled={isSubmitting}
          >
            Skip
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        </div>
      </div>
    </>
  );
};

// Styles
const styles: Record<string, React.CSSProperties> = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    backdropFilter: 'blur(4px)',
    zIndex: 1000,
    animation: 'fadeIn 0.2s ease-out',
  },
  modal: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    backgroundColor: '#ffffff',
    borderRadius: theme.borderRadius.xl,
    boxShadow: theme.shadows['2xl'],
    width: '90%',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflow: 'auto',
    zIndex: 1001,
    animation: 'slideUp 0.3s ease-out',
  },
  modalHeader: {
    padding: `${theme.spacing[6]} ${theme.spacing[6]} ${theme.spacing[4]}`,
    borderBottom: `1px solid ${theme.colors.border.light}`,
  },
  modalTitle: {
    fontFamily: theme.typography.fonts.heading,
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text.primary,
    margin: 0,
    marginBottom: theme.spacing[2],
  },
  modalSubtitle: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
    margin: 0,
  },
  modalBody: {
    padding: theme.spacing[6],
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[5],
  },
  questionGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  },
  questionLabel: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.primary,
  },
  optionsRow: {
    display: 'flex',
    gap: theme.spacing[2],
    flexWrap: 'wrap',
  },
  optionButton: {
    flex: 1,
    minWidth: '120px',
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    border: `2px solid ${theme.colors.border.default}`,
    borderRadius: theme.borderRadius.lg,
    backgroundColor: '#ffffff',
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  optionButtonSelected: {
    borderColor: theme.colors.primary[500],
    backgroundColor: theme.colors.primary[50],
    color: theme.colors.primary[700],
  },
  starsRow: {
    display: 'flex',
    gap: theme.spacing[2],
  },
  starButton: {
    background: 'none',
    border: 'none',
    padding: 0,
    cursor: 'pointer',
    transition: 'transform 0.2s ease',
  },
  starIcon: {
    fontSize: '36px',
    lineHeight: '1',
    transition: 'color 0.2s ease',
  },
  textarea: {
    width: '100%',
    padding: theme.spacing[3],
    border: `2px solid ${theme.colors.border.default}`,
    borderRadius: theme.borderRadius.lg,
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
    backgroundColor: '#ffffff',
    resize: 'vertical',
    minHeight: '80px',
    lineHeight: theme.typography.lineHeight.relaxed,
  },
  charCount: {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.text.secondary,
    textAlign: 'right',
  },
  modalFooter: {
    padding: theme.spacing[6],
    borderTop: `1px solid ${theme.colors.border.light}`,
    display: 'flex',
    gap: theme.spacing[3],
    justifyContent: 'flex-end',
  },
};
