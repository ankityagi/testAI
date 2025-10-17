import React, { type InputHTMLAttributes, type ReactNode, useState } from 'react';
import { theme } from '../../../../core/theme';

/**
 * Input Component
 * Polished styling with floating labels, focus states, error/success states, and icons
 */

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: boolean;
  icon?: ReactNode;
  fullWidth?: boolean;
  showPasswordToggle?: boolean;
  onClear?: () => void;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  success,
  icon,
  fullWidth = false,
  showPasswordToggle = false,
  onClear,
  type = 'text',
  value,
  disabled,
  style,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [shake, setShake] = useState(false);

  const hasValue = value !== '' && value !== undefined && value !== null;
  const inputType = showPasswordToggle && showPassword ? 'text' : type;

  // Trigger shake animation on error
  React.useEffect(() => {
    if (error) {
      setShake(true);
      const timer = setTimeout(() => setShake(false), 500);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const containerStyles: React.CSSProperties = {
    position: 'relative',
    width: fullWidth ? '100%' : 'auto',
    marginBottom: error ? theme.spacing[1] : 0,
  };

  const inputStyles: React.CSSProperties = {
    fontFamily: theme.typography.fonts.body,
    fontSize: theme.typography.fontSize.base,
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    paddingLeft: icon ? theme.spacing[12] : theme.spacing[4],
    paddingRight: showPasswordToggle || onClear ? theme.spacing[12] : theme.spacing[4],
    width: '100%',
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${
      error
        ? theme.colors.error[500]
        : success
          ? theme.colors.success[500]
          : isFocused
            ? theme.colors.primary[500]
            : theme.colors.border.medium
    }`,
    backgroundColor: disabled ? theme.colors.background.tertiary : theme.colors.background.primary,
    color: theme.colors.text.primary,
    outline: 'none',
    transition: theme.animations.transition.all,
    cursor: disabled ? 'not-allowed' : 'text',
    opacity: disabled ? 0.6 : 1,
    ...(shake && {
      animation: 'shake 0.5s',
    }),
  };

  const labelStyles: React.CSSProperties = {
    position: 'absolute',
    left: icon ? theme.spacing[12] : theme.spacing[4],
    top: isFocused || hasValue ? '-10px' : '50%',
    transform: isFocused || hasValue ? 'translateY(0)' : 'translateY(-50%)',
    fontSize: isFocused || hasValue ? theme.typography.fontSize.xs : theme.typography.fontSize.base,
    color: error
      ? theme.colors.error[500]
      : isFocused
        ? theme.colors.primary[500]
        : theme.colors.text.secondary,
    backgroundColor: theme.colors.background.primary,
    padding: `0 ${theme.spacing[1]}`,
    transition: theme.animations.transition.all,
    pointerEvents: 'none',
    fontWeight: theme.typography.fontWeight.medium,
  };

  const iconStyles: React.CSSProperties = {
    position: 'absolute',
    left: theme.spacing[4],
    top: '50%',
    transform: 'translateY(-50%)',
    color: error
      ? theme.colors.error[500]
      : success
        ? theme.colors.success[500]
        : theme.colors.text.secondary,
    pointerEvents: 'none',
  };

  return (
    <div style={containerStyles}>
      <div style={{ position: 'relative' }}>
        {icon && <div style={iconStyles}>{icon}</div>}

        {label && <label style={labelStyles}>{label}</label>}

        <input
          {...props}
          type={inputType}
          value={value}
          disabled={disabled}
          style={{ ...inputStyles, ...style }}
          onFocus={(e) => {
            setIsFocused(true);
            props.onFocus?.(e);
          }}
          onBlur={(e) => {
            setIsFocused(false);
            props.onBlur?.(e);
          }}
        />

        {/* Success check icon */}
        {success && !error && (
          <div
            style={{
              position: 'absolute',
              right: theme.spacing[4],
              top: '50%',
              transform: 'translateY(-50%)',
              color: theme.colors.success[500],
              fontSize: '20px',
            }}
          >
            ✓
          </div>
        )}

        {/* Password visibility toggle */}
        {showPasswordToggle && type === 'password' && !error && !success && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: 'absolute',
              right: theme.spacing[4],
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
              color: theme.colors.text.secondary,
              fontSize: '18px',
            }}
          >
            {showPassword ? '👁️' : '👁️‍🗨️'}
          </button>
        )}

        {/* Clear button */}
        {onClear && hasValue && !showPasswordToggle && !error && !success && (
          <button
            type="button"
            onClick={onClear}
            style={{
              position: 'absolute',
              right: theme.spacing[4],
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
              color: theme.colors.text.secondary,
              fontSize: '18px',
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div
          style={{
            color: theme.colors.error[500],
            fontSize: theme.typography.fontSize.sm,
            marginTop: theme.spacing[1],
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[1],
          }}
        >
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

// Add shake animation
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
      20%, 40%, 60%, 80% { transform: translateX(4px); }
    }
  `;
  document.head.appendChild(style);
}
