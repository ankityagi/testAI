import React, { type ButtonHTMLAttributes, type ReactNode } from 'react';
import { theme } from '../../../../core/theme';

/**
 * Button Component
 * Delightful interactions with smooth hover effects, scale animations, and polished styling
 */

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: ReactNode;
  fullWidth?: boolean;
  children: ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  fullWidth = false,
  disabled,
  children,
  style,
  ...props
}) => {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: theme.colors.primary[500],
          color: theme.colors.text.inverse,
          border: 'none',
          boxShadow: theme.shadows.sm,
        };
      case 'secondary':
        return {
          backgroundColor: theme.colors.secondary[500],
          color: theme.colors.text.inverse,
          border: 'none',
          boxShadow: theme.shadows.sm,
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          color: theme.colors.primary[500],
          border: `2px solid ${theme.colors.primary[500]}`,
          boxShadow: 'none',
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          color: theme.colors.text.primary,
          border: 'none',
          boxShadow: 'none',
        };
    }
  };

  const getSizeStyles = (): React.CSSProperties => {
    switch (size) {
      case 'sm':
        return {
          padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
          fontSize: theme.typography.fontSize.sm,
        };
      case 'md':
        return {
          padding: `${theme.spacing[3]} ${theme.spacing[6]}`,
          fontSize: theme.typography.fontSize.base,
        };
      case 'lg':
        return {
          padding: `${theme.spacing[4]} ${theme.spacing[8]}`,
          fontSize: theme.typography.fontSize.lg,
        };
    }
  };

  const baseStyles: React.CSSProperties = {
    fontFamily: theme.typography.fonts.body,
    fontWeight: theme.typography.fontWeight.semibold,
    borderRadius: theme.borderRadius.md,
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    transition: theme.animations.transition.transform,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing[2],
    width: fullWidth ? '100%' : 'auto',
    opacity: disabled ? 0.5 : 1,
    position: 'relative',
    ...getVariantStyles(),
    ...getSizeStyles(),
  };

  return (
    <button
      {...props}
      disabled={disabled || loading}
      style={{
        ...baseStyles,
        ...style,
      }}
      onMouseEnter={(e) => {
        if (!disabled && !loading) {
          e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
          if (variant !== 'ghost') {
            e.currentTarget.style.boxShadow = theme.shadows.hover.md;
          }
        }
        props.onMouseEnter?.(e);
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0) scale(1)';
        if (variant !== 'ghost') {
          e.currentTarget.style.boxShadow = variant === 'outline' ? 'none' : theme.shadows.sm;
        }
        props.onMouseLeave?.(e);
      }}
      onMouseDown={(e) => {
        if (!disabled && !loading) {
          e.currentTarget.style.transform = 'translateY(0) scale(0.98)';
        }
        props.onMouseDown?.(e);
      }}
      onMouseUp={(e) => {
        if (!disabled && !loading) {
          e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)';
        }
        props.onMouseUp?.(e);
      }}
    >
      {loading && (
        <div
          style={{
            width: '16px',
            height: '16px',
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.6s linear infinite',
          }}
        />
      )}
      {!loading && icon && <span>{icon}</span>}
      <span>{children}</span>
    </button>
  );
};

// Add keyframe animation for spinner
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
}
