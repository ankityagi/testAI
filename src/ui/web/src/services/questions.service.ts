/**
 * Questions Service
 * Fetch questions and submit attempts
 */

import { apiClient } from './apiClient';
import type {
  QuestionRequest,
  QuestionResponse,
  AttemptSubmission,
  AttemptResult,
} from '../types/api';

export const questionsService = {
  /**
   * Fetch questions for a child based on criteria
   */
  async fetch(request: QuestionRequest): Promise<QuestionResponse> {
    return apiClient.post<QuestionResponse>('/questions/fetch', request);
  },

  /**
   * Submit an answer attempt
   */
  async submitAttempt(attempt: AttemptSubmission): Promise<AttemptResult> {
    return apiClient.post<AttemptResult>('/attempts/', attempt);
  },

  /**
   * Get available subjects
   */
  getSubjects(): string[] {
    return ['math', 'reading', 'science', 'writing'];
  },

  /**
   * Get available topics for a subject (placeholder - will be dynamic later)
   */
  getTopics(subject: string): string[] {
    const topics: Record<string, string[]> = {
      math: ['Number & Operations', 'Algebra', 'Geometry', 'Measurement', 'Data Analysis'],
      reading: ['Reading Comprehension', 'Vocabulary', 'Literary Analysis', 'Informational Text'],
      science: ['Life Science', 'Physical Science', 'Earth Science', 'Engineering'],
      writing: ['Grammar', 'Composition', 'Mechanics', 'Research'],
    };
    return topics[subject] || [];
  },

  /**
   * Get available subtopics for a subject/topic combination
   */
  getSubtopics(subject: string, topic: string): string[] {
    const subtopics: Record<string, Record<string, string[]>> = {
      math: {
        'Number & Operations': [
          'Addition',
          'Subtraction',
          'Multiplication',
          'Division',
          'Fractions',
          'Decimals',
          'Place Value',
          'Comparing Numbers',
          'Rounding',
          'Money',
          'Divisibility',
        ],
        Algebra: [
          'Patterns',
          'Expressions',
          'Equations',
          'Variables',
          'Functions',
          'Inequalities',
        ],
        Geometry: [
          'Shapes',
          'Lines & Angles',
          'Area & Perimeter',
          'Volume',
          'Coordinates',
          'Transformations',
        ],
        Measurement: ['Length', 'Weight', 'Time', 'Temperature', 'Capacity', 'Unit Conversion'],
        'Data Analysis': [
          'Graphs',
          'Tables',
          'Mean & Median',
          'Probability',
          'Data Collection',
        ],
      },
      reading: {
        'Reading Comprehension': [
          'Main Idea',
          'Supporting Details',
          'Inference',
          'Vocabulary in Context',
          'Text Structure',
        ],
        Vocabulary: ['Word Meaning', 'Context Clues', 'Synonyms & Antonyms', 'Root Words', 'Idioms'],
        'Literary Analysis': [
          'Character Analysis',
          'Plot',
          'Theme',
          'Point of View',
          'Literary Devices',
        ],
        'Informational Text': [
          'Text Features',
          'Fact vs Opinion',
          'Cause & Effect',
          'Compare & Contrast',
        ],
      },
      science: {
        'Life Science': ['Plants', 'Animals', 'Ecosystems', 'Human Body', 'Cells', 'Genetics'],
        'Physical Science': ['Matter', 'Energy', 'Forces', 'Motion', 'Light', 'Sound'],
        'Earth Science': ['Weather', 'Rocks & Minerals', 'Water Cycle', 'Astronomy', 'Climate'],
        Engineering: ['Design Process', 'Simple Machines', 'Technology', 'Problem Solving'],
      },
      writing: {
        Grammar: ['Parts of Speech', 'Sentence Structure', 'Punctuation', 'Capitalization'],
        Composition: ['Paragraphs', 'Essays', 'Narrative', 'Persuasive', 'Descriptive'],
        Mechanics: ['Spelling', 'Usage', 'Editing', 'Revising'],
        Research: ['Sources', 'Citations', 'Note-taking', 'Organization'],
      },
    };
    return subtopics[subject]?.[topic] || [];
  },

  /**
   * Get difficulty levels
   */
  getDifficultyLevels(): string[] {
    return ['dynamic', 'easy', 'medium', 'hard'];
  },
};
