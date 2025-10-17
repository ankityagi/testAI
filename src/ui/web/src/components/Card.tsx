import React, { type ReactNode } from 'react';
import { theme } from '../../../../core/theme';

/**
 * Card Component
 * Elegant design with subtle shadows, hover effects, and optional gradient header
 */

export interface CardProps {
  children: ReactNode;
  header?: ReactNode;
  headerGradient?: boolean;
  hoverable?: boolean;
  padding?: keyof typeof theme.spacing;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  header,
  headerGradient = false,
  hoverable = false,
  padding = 6,
  className,
  style,
  onClick,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const containerStyles: React.CSSProperties = {
    backgroundColor: theme.colors.background.primary,
    borderRadius: theme.borderRadius.lg,
    boxShadow: isHovered && hoverable ? theme.shadows.hover.md : theme.shadows.base,
    transition: theme.animations.transition.all,
    overflow: 'hidden',
    cursor: onClick ? 'pointer' : 'default',
    transform: isHovered && hoverable ? 'translateY(-4px)' : 'translateY(0)',
    ...style,
  };

  const headerStyles: React.CSSProperties = {
    padding: theme.spacing[padding],
    borderBottom: headerGradient ? 'none' : `1px solid ${theme.colors.border.light}`,
    background: headerGradient ? theme.colors.gradients.primary : 'transparent',
    color: headerGradient ? theme.colors.text.inverse : theme.colors.text.primary,
    fontWeight: theme.typography.fontWeight.semibold,
    fontSize: theme.typography.fontSize.lg,
  };

  const bodyStyles: React.CSSProperties = {
    padding: theme.spacing[padding],
  };

  return (
    <div
      className={className}
      style={containerStyles}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {header && <div style={headerStyles}>{header}</div>}
      <div style={bodyStyles}>{children}</div>
    </div>
  );
};

// Import useState
import { useState } from 'react';
