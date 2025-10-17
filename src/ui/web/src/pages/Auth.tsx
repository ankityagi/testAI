/**
 * Auth Page
 * Beautiful login/signup page with smooth animations and polished design
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { theme } from '../../../../core/theme';
import { useAuth } from '../contexts';
import { Button, Input, Toast } from '../components';

type AuthMode = 'login' | 'signup';

export const Auth: React.FC = () => {
  const navigate = useNavigate();
  const { login, signup, isLoading } = useAuth();

  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Validation errors
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');

  // Success/error toast
  const [toast, setToast] = useState<{
    message: string;
    variant: 'success' | 'error';
  } | null>(null);

  const validateEmail = (value: string): boolean => {
    if (!value) {
      setEmailError('Email is required');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      setEmailError('Please enter a valid email');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePassword = (value: string): boolean => {
    if (!value) {
      setPasswordError('Password is required');
      return false;
    }
    if (value.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const validateConfirmPassword = (value: string): boolean => {
    if (mode === 'signup') {
      if (!value) {
        setConfirmPasswordError('Please confirm your password');
        return false;
      }
      if (value !== password) {
        setConfirmPasswordError('Passwords do not match');
        return false;
      }
    }
    setConfirmPasswordError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();

    // Validate all fields
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword);

    if (!isEmailValid || !isPasswordValid || !isConfirmPasswordValid) {
      return;
    }

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await signup(email, password);
      }

      // Show success toast
      setToast({
        message: mode === 'login' ? 'Welcome back!' : 'Account created successfully!',
        variant: 'success',
      });

      // Redirect to dashboard after short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    } catch {
      // Show error toast
      setToast({
        message:
          mode === 'login'
            ? 'Login failed. Please check your credentials.'
            : 'Signup failed. Please try again.',
        variant: 'error',
      });
    }
  };

  const switchMode = (): void => {
    setMode(mode === 'login' ? 'signup' : 'login');
    // Clear errors when switching
    setEmailError('');
    setPasswordError('');
    setConfirmPasswordError('');
  };

  const containerStyles: React.CSSProperties = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: theme.colors.gradients.primary,
    padding: theme.spacing[4],
  };

  const cardStyles: React.CSSProperties = {
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.xl,
    boxShadow: theme.shadows.xl,
    padding: theme.spacing[8],
    maxWidth: '450px',
    width: '100%',
    animation: 'fadeInUp 0.5s ease-out',
  };

  const headerStyles: React.CSSProperties = {
    textAlign: 'center',
    marginBottom: theme.spacing[8],
  };

  const titleStyles: React.CSSProperties = {
    ...theme.typography.styles.h1,
    fontSize: theme.typography.fontSize['3xl'],
    marginBottom: theme.spacing[2],
    background: theme.colors.gradients.primary,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  };

  const subtitleStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.secondary,
  };

  const tabContainerStyles: React.CSSProperties = {
    display: 'flex',
    gap: theme.spacing[2],
    marginBottom: theme.spacing[6],
    position: 'relative',
  };

  const tabStyles = (isActive: boolean): React.CSSProperties => ({
    flex: 1,
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    border: 'none',
    backgroundColor: 'transparent',
    color: isActive ? theme.colors.primary[500] : theme.colors.text.secondary,
    fontWeight: isActive
      ? theme.typography.fontWeight.semibold
      : theme.typography.fontWeight.medium,
    fontSize: theme.typography.fontSize.base,
    cursor: 'pointer',
    transition: theme.animations.transition.all,
    position: 'relative',
    borderBottom: `2px solid ${isActive ? theme.colors.primary[500] : 'transparent'}`,
  });

  const formStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const linkStyles: React.CSSProperties = {
    textAlign: 'center',
    marginTop: theme.spacing[4],
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  };

  const linkButtonStyles: React.CSSProperties = {
    background: 'none',
    border: 'none',
    color: theme.colors.primary[500],
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
    padding: 0,
    textDecoration: 'underline',
  };

  return (
    <div style={containerStyles}>
      <div style={cardStyles}>
        <div style={headerStyles}>
          <h1 style={titleStyles}>StudyBuddy</h1>
          <p style={subtitleStyles}>
            {mode === 'login'
              ? 'Welcome back! Ready to learn?'
              : 'Start your learning journey today'}
          </p>
        </div>

        <div style={tabContainerStyles}>
          <button
            style={tabStyles(mode === 'login')}
            onClick={() => mode !== 'login' && switchMode()}
          >
            Login
          </button>
          <button
            style={tabStyles(mode === 'signup')}
            onClick={() => mode !== 'signup' && switchMode()}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} style={formStyles}>
          <Input
            type="email"
            label="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (emailError) validateEmail(e.target.value);
            }}
            onBlur={(e) => validateEmail(e.target.value)}
            error={emailError}
            success={!emailError && email.length > 0}
            fullWidth
            disabled={isLoading}
          />

          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (passwordError) validatePassword(e.target.value);
            }}
            onBlur={(e) => validatePassword(e.target.value)}
            error={passwordError}
            success={!passwordError && password.length >= 6}
            showPasswordToggle
            fullWidth
            disabled={isLoading}
          />

          {mode === 'signup' && (
            <Input
              type="password"
              label="Confirm Password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (confirmPasswordError) validateConfirmPassword(e.target.value);
              }}
              onBlur={(e) => validateConfirmPassword(e.target.value)}
              error={confirmPasswordError}
              success={
                !confirmPasswordError && confirmPassword === password && confirmPassword.length > 0
              }
              showPasswordToggle
              fullWidth
              disabled={isLoading}
            />
          )}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={isLoading}
            disabled={isLoading}
          >
            {mode === 'login' ? 'Log In' : 'Create Account'}
          </Button>
        </form>

        <div style={linkStyles}>
          {mode === 'login' ? (
            <>
              Don't have an account?{' '}
              <button style={linkButtonStyles} onClick={switchMode}>
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button style={linkButtonStyles} onClick={switchMode}>
                Log in
              </button>
            </>
          )}
        </div>
      </div>

      {toast && (
        <Toast message={toast.message} variant={toast.variant} onDismiss={() => setToast(null)} />
      )}
    </div>
  );
};

// Add fadeInUp animation
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `;
  document.head.appendChild(style);
}
