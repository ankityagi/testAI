/**
 * TypeScript types matching backend Pydantic models
 */

export interface Parent {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  parent: Parent;
}

export interface ChildBase {
  name: string;
  birthdate?: string | null;
  grade?: number | null;
  zip?: string | null;
}

export type ChildCreate = ChildBase;

export interface ChildUpdate {
  name?: string;
  birthdate?: string | null;
  grade?: number | null;
  zip?: string | null;
}

export interface Child extends ChildBase {
  id: string;
  parent_id: string;
  created_at: string;
}

export interface QuestionRequest {
  child_id: string;
  subject: string;
  topic?: string | null;
  subtopic?: string | null;
  limit?: number;
}

export interface Question {
  id: string;
  standard_ref?: string | null;
  subject: string;
  grade?: number | null;
  topic?: string | null;
  sub_topic?: string | null;
  subtopic?: string | null; // Alias for sub_topic
  difficulty?: string | null;
  stem: string;
  options: string[];
  correct_answer: string;
  rationale?: string | null;
  source?: string | null;
  hash: string;
}

export interface QuestionResponse {
  questions: Question[];
  selected_subtopic?: string | null;
}

export interface AttemptSubmission {
  child_id: string;
  question_id: string;
  selected: string;
  time_spent_ms: number;
}

export interface AttemptResult {
  attempt_id: string;
  correct: boolean;
  expected: string;
}

export interface SubjectBreakdown {
  correct: number;
  total: number;
  accuracy: number;
}

export interface ProgressResponse {
  attempted: number;
  correct: number;
  accuracy: number;
  current_streak: number;
  by_subject: Record<string, SubjectBreakdown>;
}

export interface Standard {
  subject: string;
  grade: number;
  domain?: string | null;
  sub_domain?: string | null;
  standard_ref: string;
  title?: string | null;
  description?: string | null;
}

export interface AdminGenerateRequest {
  subject: string;
  topic?: string | null;
  grade?: number | null;
  difficulty?: string;
  count?: number;
}

export interface ApiError {
  detail: string;
  status?: number;
}
