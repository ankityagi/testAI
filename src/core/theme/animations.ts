/**
 * Animation Tokens
 * Smooth, natural animations with spring-based easing
 * Durations and timing functions for consistent motion
 */

export const animations = {
  // Durations
  duration: {
    instant: '0ms',
    fast: '150ms',
    normal: '200ms',
    moderate: '300ms',
    slow: '400ms',
    slower: '600ms',
  },

  // Easing functions (timing functions)
  easing: {
    // Standard easings
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',

    // Custom cubic-bezier for smooth, natural motion
    smooth: 'cubic-bezier(0.4, 0.0, 0.2, 1)', // Material Design standard
    snappy: 'cubic-bezier(0.4, 0.0, 0.6, 1)', // Quick but smooth
    gentle: 'cubic-bezier(0.25, 0.1, 0.25, 1)', // Very smooth
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)', // Bouncy effect

    // Spring-based (for CSS spring() when available, fallback to cubic-bezier)
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)', // Spring-like effect
    softSpring: 'cubic-bezier(0.5, 1.25, 0.75, 1.25)', // Gentle spring
  },

  // Common transitions
  transition: {
    // Micro-interactions (hover, focus, etc.)
    fast: '150ms cubic-bezier(0.4, 0.0, 0.2, 1)',
    normal: '200ms cubic-bezier(0.4, 0.0, 0.2, 1)',

    // Page transitions
    page: '300ms cubic-bezier(0.4, 0.0, 0.2, 1)',

    // Modal/overlay animations
    modal: '200ms cubic-bezier(0.4, 0.0, 0.2, 1)',

    // Smooth color changes
    color: '150ms ease-out',

    // Transform animations (scale, rotate, translate)
    transform: '200ms cubic-bezier(0.34, 1.56, 0.64, 1)',

    // Opacity fades
    fade: '200ms ease-out',

    // All properties
    all: 'all 200ms cubic-bezier(0.4, 0.0, 0.2, 1)',
  },

  // Keyframe animations (can be used with CSS @keyframes)
  keyframes: {
    // Fade in
    fadeIn: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },

    // Fade out
    fadeOut: {
      from: { opacity: 1 },
      to: { opacity: 0 },
    },

    // Slide in from bottom
    slideInUp: {
      from: { transform: 'translateY(20px)', opacity: 0 },
      to: { transform: 'translateY(0)', opacity: 1 },
    },

    // Slide in from top
    slideInDown: {
      from: { transform: 'translateY(-20px)', opacity: 0 },
      to: { transform: 'translateY(0)', opacity: 1 },
    },

    // Slide in from right
    slideInRight: {
      from: { transform: 'translateX(20px)', opacity: 0 },
      to: { transform: 'translateX(0)', opacity: 1 },
    },

    // Slide in from left
    slideInLeft: {
      from: { transform: 'translateX(-20px)', opacity: 0 },
      to: { transform: 'translateX(0)', opacity: 1 },
    },

    // Scale in
    scaleIn: {
      from: { transform: 'scale(0.9)', opacity: 0 },
      to: { transform: 'scale(1)', opacity: 1 },
    },

    // Shake (for error states)
    shake: {
      '0%, 100%': { transform: 'translateX(0)' },
      '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
      '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
    },

    // Pulse (for loading or attention)
    pulse: {
      '0%, 100%': { opacity: 1 },
      '50%': { opacity: 0.5 },
    },

    // Spin (for loading spinners)
    spin: {
      from: { transform: 'rotate(0deg)' },
      to: { transform: 'rotate(360deg)' },
    },

    // Bounce (for success celebrations)
    bounce: {
      '0%, 100%': { transform: 'translateY(0)' },
      '50%': { transform: 'translateY(-10px)' },
    },
  },
} as const;

export type Animations = typeof animations;
