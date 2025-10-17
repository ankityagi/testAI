/**
 * Standards Panel Component
 * Displays Common Core and state standards organized by subject and grade
 */

import React, { useEffect, useState } from 'react';
import { theme } from '../../../../../core/theme';
import { LoadingSpinner, Toast } from '..';
import { standardsService } from '../../services';
import type { Standard, ApiError } from '../../types/api';

export const StandardsPanel: React.FC = () => {
  const [standards, setStandards] = useState<Standard[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [selectedGrade, setSelectedGrade] = useState<number | 'all'>('all');

  useEffect(() => {
    const fetchStandards = async (): Promise<void> => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await standardsService.list();
        setStandards(data);
      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError.detail || 'Failed to load standards');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStandards();
  }, []);

  // Filter standards
  const filteredStandards = standards.filter((standard) => {
    if (selectedSubject !== 'all' && standard.subject !== selectedSubject) {
      return false;
    }
    if (selectedGrade !== 'all' && standard.grade !== selectedGrade) {
      return false;
    }
    return true;
  });

  // Group by subject then grade
  const groupedStandards: Record<
    string,
    Record<number, Standard[]>
  > = standardsService.groupBySubjectAndGrade(filteredStandards);

  // Get unique subjects and grades for filters
  const subjects = ['all', ...new Set(standards.map((s) => s.subject))];
  const grades = ['all', ...new Set(standards.map((s) => s.grade))].sort();

  // Styles
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const filtersStyles: React.CSSProperties = {
    display: 'flex',
    gap: theme.spacing[3],
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
  };

  const filterGroupStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
    flex: 1,
  };

  const labelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
  };

  const selectStyles: React.CSSProperties = {
    padding: theme.spacing[2],
    fontSize: theme.typography.fontSize.base,
    borderRadius: theme.borderRadius.sm,
    border: `1px solid ${theme.colors.border.light}`,
    backgroundColor: theme.colors.background.primary,
    outline: 'none',
    transition: theme.animations.transition.all,
  };

  const standardsListStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[4],
  };

  const subjectSectionStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[3],
  };

  const subjectHeaderStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.semibold,
    textTransform: 'capitalize',
    color: theme.colors.primary[600],
    marginBottom: theme.spacing[2],
  };

  const gradeGroupStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing[2],
    marginLeft: theme.spacing[4],
  };

  const gradeHeaderStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.primary,
  };

  const standardCardStyles: React.CSSProperties = {
    padding: theme.spacing[4],
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    marginLeft: theme.spacing[4],
    border: `1px solid ${theme.colors.border.light}`,
  };

  const standardRefStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.primary[500],
    marginBottom: theme.spacing[2],
  };

  const standardTitleStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    marginBottom: theme.spacing[2],
  };

  const standardDescriptionStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.secondary,
    lineHeight: 1.6,
  };

  const domainBadgeStyles: React.CSSProperties = {
    display: 'inline-block',
    padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
    backgroundColor: theme.colors.primary[100],
    color: theme.colors.primary[700],
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.fontSize.xs,
    fontWeight: theme.typography.fontWeight.medium,
    marginBottom: theme.spacing[2],
  };

  const emptyStateStyles: React.CSSProperties = {
    textAlign: 'center',
    padding: theme.spacing[8],
    color: theme.colors.text.secondary,
  };

  const countBadgeStyles: React.CSSProperties = {
    display: 'inline-block',
    padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
    backgroundColor: theme.colors.background.secondary,
    color: theme.colors.text.secondary,
    borderRadius: theme.borderRadius.sm,
    fontSize: theme.typography.fontSize.sm,
    marginLeft: theme.spacing[2],
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: theme.spacing[6] }}>
        <LoadingSpinner size="md" label="Loading standards..." />
      </div>
    );
  }

  if (standards.length === 0 && !error) {
    return (
      <div style={emptyStateStyles}>
        <div style={{ fontSize: '48px', marginBottom: theme.spacing[3] }}>📚</div>
        <p>No standards available</p>
      </div>
    );
  }

  return (
    <div style={containerStyles}>
      {/* Filters */}
      <div style={filtersStyles}>
        <div style={filterGroupStyles}>
          <label style={labelStyles}>Subject</label>
          <select
            style={selectStyles}
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            {subjects.map((subject) => (
              <option key={subject} value={subject}>
                {subject === 'all'
                  ? 'All Subjects'
                  : subject.charAt(0).toUpperCase() + subject.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div style={filterGroupStyles}>
          <label style={labelStyles}>Grade</label>
          <select
            style={selectStyles}
            value={selectedGrade}
            onChange={(e) =>
              setSelectedGrade(e.target.value === 'all' ? 'all' : parseInt(e.target.value, 10))
            }
          >
            {grades.map((grade) => (
              <option key={grade} value={grade}>
                {grade === 'all' ? 'All Grades' : `Grade ${grade}`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results count */}
      {filteredStandards.length > 0 && (
        <div style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
          Showing {filteredStandards.length} standard{filteredStandards.length === 1 ? '' : 's'}
        </div>
      )}

      {/* Standards List */}
      {filteredStandards.length === 0 ? (
        <div style={emptyStateStyles}>
          <p>No standards match the selected filters</p>
        </div>
      ) : (
        <div style={standardsListStyles}>
          {Object.entries(groupedStandards).map(
            ([subject, gradeGroups]: [string, Record<number, Standard[]>]) => (
              <div key={subject} style={subjectSectionStyles}>
                <h3 style={subjectHeaderStyles}>
                  {subject}
                  <span style={countBadgeStyles}>{Object.values(gradeGroups).flat().length}</span>
                </h3>

                {Object.entries(gradeGroups)
                  .sort(([a], [b]) => parseInt(a, 10) - parseInt(b, 10))
                  .map(([grade, standardsList]: [string, Standard[]]) => (
                    <div key={grade} style={gradeGroupStyles}>
                      <h4 style={gradeHeaderStyles}>
                        Grade {grade}
                        <span style={countBadgeStyles}>{standardsList.length}</span>
                      </h4>

                      {standardsList.map((standard: Standard) => (
                        <div key={standard.standard_ref} style={standardCardStyles}>
                          <div style={standardRefStyles}>{standard.standard_ref}</div>

                          {standard.domain && (
                            <div style={domainBadgeStyles}>
                              {standard.domain}
                              {standard.sub_domain && ` › ${standard.sub_domain}`}
                            </div>
                          )}

                          {standard.title && (
                            <div style={standardTitleStyles}>{standard.title}</div>
                          )}

                          {standard.description && (
                            <div style={standardDescriptionStyles}>{standard.description}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  ))}
              </div>
            )
          )}
        </div>
      )}

      {error && <Toast message={error} variant="error" onDismiss={() => setError(null)} />}
    </div>
  );
};
