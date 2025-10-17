/**
 * Design System Theme
 * Centralized export of all design tokens
 */

export { colors } from './colors';
export type { ColorPalette } from './colors';

export { spacing } from './spacing';
export type { Spacing } from './spacing';

export { typography } from './typography';
export type { Typography } from './typography';

export { animations } from './animations';
export type { Animations } from './animations';

export { shadows } from './shadows';
export type { Shadows } from './shadows';

export { borderRadius } from './borderRadius';
export type { BorderRadius } from './borderRadius';

// Complete theme object
import { colors } from './colors';
import { spacing } from './spacing';
import { typography } from './typography';
import { animations } from './animations';
import { shadows } from './shadows';
import { borderRadius } from './borderRadius';

export const theme = {
  colors,
  spacing,
  typography,
  animations,
  shadows,
  borderRadius,
} as const;

export type Theme = typeof theme;
