# Design System Theme

Modern, iOS-inspired design tokens for the StudyBuddy application.

## Overview

This design system provides a comprehensive set of design tokens including colors, typography, spacing, animations, shadows, and border radius. All tokens are carefully crafted for visual appeal, accessibility, and consistency.

## Usage

### Importing Tokens

```typescript
import { colors, spacing, typography, animations, shadows, borderRadius } from '@/core/theme';

// Or import the complete theme
import { theme } from '@/core/theme';
```

### Using Theme Context

```typescript
import { useTheme } from '@/core/theme/ThemeProvider';

function MyComponent() {
  const { theme } = useTheme();

  return (
    <div style={{ color: theme.colors.primary[500] }}>
      Hello World
    </div>
  );
}
```

## Design Tokens

### Colors

**iOS-inspired color palette** with vibrant, accessible colors.

#### Primary Colors
- **Primary Blue**: `#007AFF` (iOS system blue)
- **Secondary Purple**: `#AF52DE` (iOS purple)
- **Success Green**: `#34C759` (iOS green)
- **Error Red**: `#FF3B30` (iOS red)
- **Warning Orange**: `#FF9500` (iOS orange)
- **Info Teal**: `#5AC8FA` (iOS teal)

Each color has shades from 50 (lightest) to 900 (darkest).

#### Subject Colors
- Math: Orange `#FF9500`
- Reading: Purple `#AF52DE`
- Science: Green `#34C759`
- Writing: Blue `#007AFF`

#### Semantic Colors
- Background (primary, secondary, tertiary)
- Text (primary, secondary, tertiary, disabled, inverse)
- Border (light, medium, dark)

#### Gradients
Pre-defined gradients for special effects:
- Primary, Secondary, Success, Warm, Cool

### Typography

**Modern, readable fonts** optimized for web and mobile.

#### Font Families
- **Body**: System fonts with Inter fallback
- **Heading**: Same as body for consistency
- **Mono**: Monospace for code

#### Font Sizes
- `xs` (12px) → `7xl` (72px)
- All sizes use rem units for accessibility

#### Font Weights
- Light (300), Normal (400), Medium (500), Semibold (600), Bold (700)

#### Text Styles
Pre-configured styles for common use cases:
- `h1`, `h2`, `h3`, `h4`, `h5`, `h6`
- `body`, `bodySmall`, `caption`
- `button`, `label`

### Spacing

**4px base unit** for consistent spacing throughout the app.

Scale: `0` → `64` (0px → 256px)

Common values:
- `2` = 8px (tight spacing)
- `4` = 16px (standard spacing)
- `6` = 24px (comfortable spacing)
- `8` = 32px (generous spacing)

### Animations

**Smooth, natural animations** with spring-based easing.

#### Durations
- `fast`: 150ms (micro-interactions)
- `normal`: 200ms (standard transitions)
- `moderate`: 300ms (page transitions)
- `slow`: 400ms (complex animations)

#### Easing Functions
- `smooth`: Material Design standard
- `snappy`: Quick but smooth
- `gentle`: Very smooth
- `bounce`: Bouncy effect
- `spring`: Spring-like effect

#### Pre-configured Transitions
- `fast`, `normal`, `page`, `modal`, `color`, `transform`, `fade`

#### Keyframe Animations
- Fade: `fadeIn`, `fadeOut`
- Slide: `slideInUp`, `slideInDown`, `slideInRight`, `slideInLeft`
- Scale: `scaleIn`
- Effects: `shake`, `pulse`, `spin`, `bounce`

### Shadows

**Subtle, soft shadows** for depth and elevation.

#### Standard Shadows
- `xs`: Subtle hint
- `sm`: Cards at rest
- `base`: Default card
- `md`: Elevated cards
- `lg`: Dropdowns, popovers
- `xl`: Modals, drawers
- `2xl`: High elevation

#### Hover Shadows
Lifted shadows for interactive states

#### Colored Shadows
Emphasis shadows for primary, success, error, warning

#### Focus Rings
Accessibility-focused ring styles

### Border Radius

**Rounded corners** for friendly, modern feel.

- `xs`: 4px (subtle)
- `sm`: 8px (buttons, inputs)
- `base`: 12px (default cards)
- `md`: 16px (medium cards)
- `lg`: 24px (large cards)
- `xl`: 32px (extra large)
- `2xl`: 48px (very rounded)
- `full`: 9999px (pills, circles)

## Design Principles

1. **Visual Appeal**: Modern, iOS-inspired design that feels polished and delightful
2. **Accessibility**: WCAG AA compliant colors (4.5:1 contrast ratio)
3. **Consistency**: All tokens follow a systematic scale
4. **Performance**: Optimized for fast rendering and smooth animations
5. **Flexibility**: Tokens can be composed for any use case

## Examples

### Button with Theme Tokens

```typescript
const Button = styled.button`
  background-color: ${theme.colors.primary[500]};
  color: ${theme.colors.text.inverse};
  padding: ${theme.spacing[3]} ${theme.spacing[6]};
  border-radius: ${theme.borderRadius.md};
  font-family: ${theme.typography.fonts.body};
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.semibold};
  box-shadow: ${theme.shadows.md};
  transition: ${theme.animations.transition.normal};

  &:hover {
    box-shadow: ${theme.shadows.hover.md};
    transform: translateY(-2px);
  }
`;
```

### Card with Animation

```typescript
const Card = styled.div`
  background: ${theme.colors.background.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing[6]};
  box-shadow: ${theme.shadows.base};
  animation: ${theme.animations.keyframes.slideInUp};
  animation-duration: ${theme.animations.duration.moderate};
  animation-timing-function: ${theme.animations.easing.spring};
`;
```

## Future Enhancements

- Dark mode support
- Responsive typography scales
- Additional color palettes
- Custom theme overrides
- Animation presets
