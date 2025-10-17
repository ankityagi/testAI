import React from 'react';
import { theme } from '../../../../core/theme';

/**
 * Theme Demo Page
 * Visual reference for all design tokens
 */

export const ThemeDemo: React.FC = () => {
  return (
    <div style={{ padding: '2rem', fontFamily: theme.typography.fonts.body }}>
      <h1 style={{ ...theme.typography.styles.h1, marginBottom: theme.spacing[8] }}>
        Design System Tokens
      </h1>

      {/* Colors */}
      <section style={{ marginBottom: theme.spacing[12] }}>
        <h2 style={{ ...theme.typography.styles.h2, marginBottom: theme.spacing[4] }}>Colors</h2>

        {/* Primary Colors */}
        <h3 style={{ ...theme.typography.styles.h3, marginTop: theme.spacing[6] }}>
          Primary (iOS Blue)
        </h3>
        <div style={{ display: 'flex', gap: theme.spacing[2], flexWrap: 'wrap' }}>
          {Object.entries(theme.colors.primary).map(([shade, color]) => (
            <div key={shade} style={{ textAlign: 'center' }}>
              <div
                style={{
                  width: '80px',
                  height: '80px',
                  backgroundColor: color,
                  borderRadius: theme.borderRadius.md,
                  boxShadow: theme.shadows.base,
                }}
              />
              <p style={{ fontSize: theme.typography.fontSize.sm, marginTop: theme.spacing[2] }}>
                {shade}
                <br />
                {color}
              </p>
            </div>
          ))}
        </div>

        {/* Subject Colors */}
        <h3 style={{ ...theme.typography.styles.h3, marginTop: theme.spacing[8] }}>
          Subject Colors
        </h3>
        <div style={{ display: 'flex', gap: theme.spacing[4], flexWrap: 'wrap' }}>
          {Object.entries(theme.colors.subjects).map(([subject, color]) => (
            <div key={subject} style={{ textAlign: 'center' }}>
              <div
                style={{
                  width: '100px',
                  height: '100px',
                  backgroundColor: color,
                  borderRadius: theme.borderRadius.lg,
                  boxShadow: theme.shadows.md,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: theme.typography.fontWeight.bold,
                }}
              >
                {subject}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Typography */}
      <section style={{ marginBottom: theme.spacing[12] }}>
        <h2 style={{ ...theme.typography.styles.h2, marginBottom: theme.spacing[4] }}>
          Typography
        </h2>
        <div style={{ ...theme.typography.styles.h1 }}>Heading 1</div>
        <div style={{ ...theme.typography.styles.h2 }}>Heading 2</div>
        <div style={{ ...theme.typography.styles.h3 }}>Heading 3</div>
        <div style={{ ...theme.typography.styles.h4 }}>Heading 4</div>
        <div style={{ ...theme.typography.styles.body, marginTop: theme.spacing[4] }}>
          Body text - The quick brown fox jumps over the lazy dog
        </div>
        <div style={{ ...theme.typography.styles.bodySmall }}>
          Small body text - The quick brown fox jumps over the lazy dog
        </div>
        <div style={{ ...theme.typography.styles.caption, marginTop: theme.spacing[2] }}>
          Caption text - The quick brown fox jumps over the lazy dog
        </div>
      </section>

      {/* Spacing */}
      <section style={{ marginBottom: theme.spacing[12] }}>
        <h2 style={{ ...theme.typography.styles.h2, marginBottom: theme.spacing[4] }}>Spacing</h2>
        <div>
          {[2, 4, 6, 8, 12, 16].map((size) => (
            <div key={size} style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
              <span style={{ width: '60px', fontSize: theme.typography.fontSize.sm }}>
                {size} ({theme.spacing[size as keyof typeof theme.spacing]})
              </span>
              <div
                style={{
                  width: theme.spacing[size as keyof typeof theme.spacing],
                  height: '20px',
                  backgroundColor: theme.colors.primary[500],
                  borderRadius: theme.borderRadius.sm,
                }}
              />
            </div>
          ))}
        </div>
      </section>

      {/* Shadows */}
      <section style={{ marginBottom: theme.spacing[12] }}>
        <h2 style={{ ...theme.typography.styles.h2, marginBottom: theme.spacing[4] }}>Shadows</h2>
        <div style={{ display: 'flex', gap: theme.spacing[6], flexWrap: 'wrap' }}>
          {['sm', 'base', 'md', 'lg', 'xl'].map((shadow) => (
            <div key={shadow} style={{ textAlign: 'center' }}>
              <div
                style={{
                  width: '120px',
                  height: '120px',
                  backgroundColor: 'white',
                  borderRadius: theme.borderRadius.lg,
                  boxShadow: theme.shadows[shadow as keyof typeof theme.shadows] as string,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: theme.typography.fontWeight.medium,
                }}
              >
                {shadow}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Border Radius */}
      <section style={{ marginBottom: theme.spacing[12] }}>
        <h2 style={{ ...theme.typography.styles.h2, marginBottom: theme.spacing[4] }}>
          Border Radius
        </h2>
        <div style={{ display: 'flex', gap: theme.spacing[4], flexWrap: 'wrap' }}>
          {['sm', 'base', 'md', 'lg', 'xl', 'full'].map((radius) => (
            <div key={radius} style={{ textAlign: 'center' }}>
              <div
                style={{
                  width: '100px',
                  height: '100px',
                  backgroundColor: theme.colors.secondary[400],
                  borderRadius: theme.borderRadius[radius as keyof typeof theme.borderRadius],
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: theme.typography.fontWeight.medium,
                }}
              >
                {radius}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
