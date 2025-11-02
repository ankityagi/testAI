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
  session_id?: string | null;
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

// Session tracking types
export interface Session {
  id: string;
  child_id: string;
  subject?: string | null;
  topic?: string | null;
  subtopic?: string | null;
  started_at: string;
  ended_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SessionSummary {
  session: Session;
  questions_attempted: number;
  questions_correct: number;
  accuracy: number; // Integer percentage 0-100
  total_time_ms: number;
  avg_time_per_question_ms: number;
  subjects_practiced: string[];
}

// Quiz Mode Types

export interface DifficultyMix {
  easy: number;
  medium: number;
  hard: number;
}

export interface QuizCreateRequest {
  child_id: string;
  subject: string;
  topic: string;
  subtopic?: string | null;
  question_count: number;
  duration_sec: number;
  difficulty_mix?: DifficultyMix | null;
}

export interface QuizSession {
  id: string;
  child_id: string;
  subject: string;
  topic: string;
  subtopic?: string | null;
  status: 'active' | 'completed' | 'expired';
  duration_sec: number;
  difficulty_mix_config: DifficultyMix;
  started_at: string;
  submitted_at?: string | null;
  score?: number | null; // Percentage 0-100
  total_questions: number;
  created_at: string;
}

export interface QuizQuestionDisplay {
  id: string;
  index: number;
  stem: string;
  options: string[];
  difficulty?: string | null;
  subject: string;
  topic?: string | null;
}

export interface QuizSessionResponse {
  session: QuizSession;
  questions: QuizQuestionDisplay[];
  time_remaining_sec?: number | null;
}

export interface QuizAnswerSubmission {
  question_id: string;
  selected_choice: string;
}

export interface QuizSubmitRequest {
  answers: QuizAnswerSubmission[];
}

export interface QuizIncorrectItem {
  question_id: string;
  index: number;
  stem: string;
  options: string[];
  selected_choice: string;
  correct_choice: string;
  explanation: string;
}

export interface QuizResult {
  session_id: string;
  score: number; // Percentage 0-100
  correct_count: number;
  total_questions: number;
  time_taken_sec: number;
  incorrect_items: QuizIncorrectItem[];
  submitted_at: string;
}
