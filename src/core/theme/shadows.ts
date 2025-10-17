/**
 * Shadow Tokens
 * Subtle, soft shadows for depth and elevation
 * Inspired by modern design systems (Material Design, iOS)
 */

export const shadows = {
  // No shadow
  none: 'none',

  // Extra small - Subtle hint of depth
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',

  // Small - Cards at rest
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',

  // Base - Default card shadow
  base: '0 2px 4px -1px rgba(0, 0, 0, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.1)',

  // Medium - Elevated cards
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',

  // Large - Dropdowns, popovers
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',

  // Extra large - Modals, drawers
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',

  // 2XL - High elevation components
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

  // Inner shadow - Inset effect
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',

  // Hover states - Lifted shadow
  hover: {
    sm: '0 4px 8px -2px rgba(0, 0, 0, 0.15), 0 2px 4px -1px rgba(0, 0, 0, 0.1)',
    md: '0 8px 12px -2px rgba(0, 0, 0, 0.15), 0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 16px 24px -4px rgba(0, 0, 0, 0.15), 0 8px 12px -2px rgba(0, 0, 0, 0.1)',
  },

  // Colored shadows for emphasis
  colored: {
    primary: '0 10px 15px -3px rgba(0, 122, 255, 0.3), 0 4px 6px -2px rgba(0, 122, 255, 0.2)',
    success: '0 10px 15px -3px rgba(52, 199, 89, 0.3), 0 4px 6px -2px rgba(52, 199, 89, 0.2)',
    error: '0 10px 15px -3px rgba(255, 59, 48, 0.3), 0 4px 6px -2px rgba(255, 59, 48, 0.2)',
    warning: '0 10px 15px -3px rgba(255, 149, 0, 0.3), 0 4px 6px -2px rgba(255, 149, 0, 0.2)',
  },

  // Focus ring (for accessibility)
  focus: {
    default: '0 0 0 3px rgba(0, 122, 255, 0.3)',
    error: '0 0 0 3px rgba(255, 59, 48, 0.3)',
    success: '0 0 0 3px rgba(52, 199, 89, 0.3)',
  },
} as const;

export type Shadows = typeof shadows;
