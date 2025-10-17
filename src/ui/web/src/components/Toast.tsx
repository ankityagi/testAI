import React, { useEffect, useState } from 'react';
import { theme } from '../../../../core/theme';

/**
 * Toast Component
 * Notification with slide-in animation, auto-dismiss, and progress bar
 */

export type ToastVariant = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  message: string;
  variant?: ToastVariant;
  duration?: number; // milliseconds
  onDismiss?: () => void;
  style?: React.CSSProperties;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  variant = 'info',
  duration = 5000,
  onDismiss,
  style,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    // Slide in
    setTimeout(() => setIsVisible(true), 10);

    // Progress bar countdown
    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.max(0, prev - (100 / duration) * 50));
    }, 50);

    // Auto-dismiss
    const dismissTimer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onDismiss?.(), 300);
    }, duration);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(dismissTimer);
    };
  }, [duration, onDismiss]);

  const getVariantStyles = () => {
    switch (variant) {
      case 'success':
        return {
          backgroundColor: theme.colors.success[50],
          borderColor: theme.colors.success[500],
          color: theme.colors.success[700],
          icon: '✓',
        };
      case 'error':
        return {
          backgroundColor: theme.colors.error[50],
          borderColor: theme.colors.error[500],
          color: theme.colors.error[700],
          icon: '✕',
        };
      case 'warning':
        return {
          backgroundColor: theme.colors.warning[50],
          borderColor: theme.colors.warning[500],
          color: theme.colors.warning[700],
          icon: '⚠',
        };
      case 'info':
      default:
        return {
          backgroundColor: theme.colors.info[50],
          borderColor: theme.colors.info[500],
          color: theme.colors.info[700],
          icon: 'ℹ',
        };
    }
  };

  const variantStyles = getVariantStyles();

  const containerStyles: React.CSSProperties = {
    position: 'fixed',
    top: theme.spacing[6],
    right: theme.spacing[6],
    zIndex: 9999,
    minWidth: '300px',
    maxWidth: '500px',
    backgroundColor: variantStyles.backgroundColor,
    border: `2px solid ${variantStyles.borderColor}`,
    borderRadius: theme.borderRadius.lg,
    boxShadow: theme.shadows.xl,
    overflow: 'hidden',
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
    transition: theme.animations.transition.all,
    ...style,
  };

  const contentStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[3],
    padding: `${theme.spacing[4]} ${theme.spacing[4]}`,
    color: variantStyles.color,
  };

  const progressBarStyles: React.CSSProperties = {
    height: '4px',
    backgroundColor: variantStyles.borderColor,
    width: `${progress}%`,
    transition: 'width 50ms linear',
  };

  return (
    <div style={containerStyles} role="alert">
      <div style={contentStyles}>
        <span style={{ fontSize: '24px' }}>{variantStyles.icon}</span>
        <span style={{ flex: 1, fontWeight: theme.typography.fontWeight.medium }}>{message}</span>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(() => onDismiss?.(), 300);
          }}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            color: variantStyles.color,
            fontSize: '24px',
            lineHeight: 1,
          }}
        >
          ×
        </button>
      </div>
      <div style={progressBarStyles} />
    </div>
  );
};
