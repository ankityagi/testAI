import React, { useEffect, useState } from 'react';
import { theme } from '../../../../core/theme';

/**
 * ErrorMessage Component
 * Attention-grabbing but friendly error display with slide-in animation
 */

export interface ErrorMessageProps {
  message: string;
  icon?: string;
  onDismiss?: () => void;
  style?: React.CSSProperties;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  icon = '⚠️',
  onDismiss,
  style,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger slide-in animation
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[2],
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    backgroundColor: theme.colors.error[50],
    border: `1px solid ${theme.colors.error[500]}`,
    borderRadius: theme.borderRadius.md,
    color: theme.colors.error[700],
    fontSize: theme.typography.fontSize.sm,
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translateY(0)' : 'translateY(-10px)',
    transition: theme.animations.transition.all,
    ...style,
  };

  return (
    <div style={containerStyles} role="alert">
      <span style={{ fontSize: '18px' }}>{icon}</span>
      <span style={{ flex: 1 }}>{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            color: theme.colors.error[700],
            fontSize: '20px',
            lineHeight: 1,
          }}
        >
          ×
        </button>
      )}
    </div>
  );
};
