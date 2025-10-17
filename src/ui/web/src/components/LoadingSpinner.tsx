import React from 'react';
import { theme } from '../../../../core/theme';

/**
 * LoadingSpinner Component
 * Modern spinner design with smooth animation
 */

export type SpinnerSize = 'sm' | 'md' | 'lg';
export type SpinnerVariant = 'primary' | 'secondary' | 'white';

export interface LoadingSpinnerProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
  label?: string;
  style?: React.CSSProperties;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  label,
  style,
}) => {
  const getSizeValue = (): string => {
    switch (size) {
      case 'sm':
        return '24px';
      case 'md':
        return '40px';
      case 'lg':
        return '60px';
    }
  };

  const getColor = (): string => {
    switch (variant) {
      case 'primary':
        return theme.colors.primary[500];
      case 'secondary':
        return theme.colors.secondary[500];
      case 'white':
        return theme.colors.text.inverse;
    }
  };

  const sizeValue = getSizeValue();
  const color = getColor();

  const containerStyles: React.CSSProperties = {
    display: 'inline-flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing[2],
    ...style,
  };

  const spinnerStyles: React.CSSProperties = {
    width: sizeValue,
    height: sizeValue,
    border: `3px solid ${theme.colors.gray[200]}`,
    borderTopColor: color,
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  };

  return (
    <div style={containerStyles}>
      <div style={spinnerStyles} />
      {label && (
        <span
          style={{
            fontSize: theme.typography.fontSize.sm,
            color: theme.colors.text.secondary,
          }}
        >
          {label}
        </span>
      )}
    </div>
  );
};
