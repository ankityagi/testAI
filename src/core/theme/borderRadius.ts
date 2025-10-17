/**
 * Border Radius Tokens
 * Rounded corners for friendly, modern feel
 * Inspired by iOS and modern design systems
 */

export const borderRadius = {
  none: '0',
  xs: '0.25rem', // 4px - Subtle rounding
  sm: '0.5rem', // 8px - Small buttons, inputs
  base: '0.75rem', // 12px - Default cards
  md: '1rem', // 16px - Medium cards, modals
  lg: '1.5rem', // 24px - Large cards, panels
  xl: '2rem', // 32px - Extra large components
  '2xl': '3rem', // 48px - Very rounded
  full: '9999px', // Fully rounded (pills, circles)
} as const;

export type BorderRadius = typeof borderRadius;
