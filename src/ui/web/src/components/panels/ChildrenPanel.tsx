/**
 * Children Panel Component
 * Displays children list and add child form
 */

import React, { useState } from 'react';
import { theme } from '../../../../../core/theme';
import { useChildren } from '../../contexts';
import { Button, Input, LoadingSpinner, Toast } from '..';
import type { ChildCreate } from '../../types/api';

export const ChildrenPanel: React.FC = () => {
  const { children, selectedChild, selectChild, addChild, isLoading } = useChildren();

  const [showAddForm, setShowAddForm] = useState(false);
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('');
  const [zip, setZip] = useState('');
  const [nameError, setNameError] = useState('');
  const [gradeError, setGradeError] = useState('');
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(
    null
  );

  const validateName = (value: string): boolean => {
    if (!value.trim()) {
      setNameError('Name is required');
      return false;
    }
    setNameError('');
    return true;
  };

  const validateGrade = (value: string): boolean => {
    if (!value) {
      setGradeError('Grade is required');
      return false;
    }
    const gradeNum = parseInt(value, 10);
    if (isNaN(gradeNum) || gradeNum < 0 || gradeNum > 12) {
      setGradeError('Grade must be between 0 and 12');
      return false;
    }
    setGradeError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();

    const isNameValid = validateName(name);
    const isGradeValid = validateGrade(grade);

    if (!isNameValid || !isGradeValid) {
      return;
    }

    try {
      const childData: ChildCreate = {
        name: name.trim(),
        grade: parseInt(grade, 10),
        zip: zip.trim() || null,
      };

      const newChild = await addChild(childData);
      setToast({ message: `${newChild.name} added successfully!`, variant: 'success' });

      // Reset form
      setName('');
      setGrade('');
      setZip('');
      setShowAddForm(false);

      // Auto-select the new child
      selectChild(newChild);
    } catch {
      setToast({ message: 'Failed to add child. Please try again.', variant: 'error' });
    }
  };

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const childListStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  };

  const childCardStyles = (isSelected: boolean): React.CSSProperties => ({
    padding: theme.spacing[4],
    border: `2px solid ${isSelected ? theme.colors.primary[500] : theme.colors.border.light}`,
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    transition: theme.animations.transition.all,
    backgroundColor: isSelected ? theme.colors.primary[50] : theme.colors.background.primary,
  });

  const childNameStyles: React.CSSProperties = {
    ...theme.typography.styles.h4,
    fontSize: theme.typography.fontSize.lg,
    marginBottom: theme.spacing[1],
  };

  const childInfoStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
  };

  const formStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
  };

  const emptyStateStyles: React.CSSProperties = {
    textAlign: 'center',
    padding: theme.spacing[6],
    color: theme.colors.text.secondary,
  };

  return (
    <div style={containerStyles}>
      {isLoading && children.length === 0 ? (
        <div style={{ textAlign: 'center', padding: theme.spacing[6] }}>
          <LoadingSpinner size="md" label="Loading children..." />
        </div>
      ) : (
        <>
          {children.length > 0 ? (
            <div style={childListStyles}>
              {children.map((child) => (
                <div
                  key={child.id}
                  style={childCardStyles(selectedChild?.id === child.id)}
                  onClick={() => selectChild(child)}
                  onMouseEnter={(e) => {
                    if (selectedChild?.id !== child.id) {
                      e.currentTarget.style.borderColor = theme.colors.primary[300];
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = theme.shadows.sm;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedChild?.id !== child.id) {
                      e.currentTarget.style.borderColor = theme.colors.border.light;
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                    }
                  }}
                >
                  <div style={childNameStyles}>{child.name}</div>
                  <div style={childInfoStyles}>
                    Grade {child.grade !== null ? child.grade : 'Not specified'}
                    {child.zip && ` • ${child.zip}`}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={emptyStateStyles}>
              <p>No children added yet. Click "Add Child" to get started!</p>
            </div>
          )}

          {!showAddForm ? (
            <Button
              variant="primary"
              fullWidth
              onClick={() => setShowAddForm(true)}
              disabled={isLoading}
            >
              + Add Child
            </Button>
          ) : (
            <form onSubmit={handleSubmit} style={formStyles}>
              <h4 style={theme.typography.styles.h4}>Add New Child</h4>

              <Input
                label="Child's Name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (nameError) validateName(e.target.value);
                }}
                onBlur={(e) => validateName(e.target.value)}
                error={nameError}
                success={!nameError && name.length > 0}
                fullWidth
                disabled={isLoading}
              />

              <Input
                label="Grade (0-12)"
                type="number"
                value={grade}
                onChange={(e) => {
                  setGrade(e.target.value);
                  if (gradeError) validateGrade(e.target.value);
                }}
                onBlur={(e) => validateGrade(e.target.value)}
                error={gradeError}
                success={!gradeError && grade.length > 0}
                fullWidth
                disabled={isLoading}
              />

              <Input
                label="ZIP Code (Optional)"
                value={zip}
                onChange={(e) => setZip(e.target.value)}
                fullWidth
                disabled={isLoading}
              />

              <div style={{ display: 'flex', gap: theme.spacing[2] }}>
                <Button
                  type="button"
                  variant="ghost"
                  fullWidth
                  onClick={() => {
                    setShowAddForm(false);
                    setName('');
                    setGrade('');
                    setZip('');
                    setNameError('');
                    setGradeError('');
                  }}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  loading={isLoading}
                  disabled={isLoading}
                >
                  Save Child
                </Button>
              </div>
            </form>
          )}
        </>
      )}

      {toast && (
        <Toast message={toast.message} variant={toast.variant} onDismiss={() => setToast(null)} />
      )}
    </div>
  );
};
