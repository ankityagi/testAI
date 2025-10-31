-- Migration: Add quiz_sessions and quiz_session_questions tables
-- Description: Adds support for timed quiz mode with fixed question sets
-- Created: 2025-10-31

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum type for quiz session status
DO $$ BEGIN
  CREATE TYPE quiz_status AS ENUM ('active', 'completed', 'expired');
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- Create quiz_sessions table
CREATE TABLE IF NOT EXISTS quiz_sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  child_id uuid NOT NULL REFERENCES children(id) ON DELETE CASCADE,
  subject text NOT NULL,
  topic text NOT NULL,
  subtopic text,
  status quiz_status NOT NULL DEFAULT 'active',
  duration_sec integer NOT NULL CHECK (duration_sec >= 300 AND duration_sec <= 7200),
  difficulty_mix_config jsonb NOT NULL DEFAULT '{"easy": 0.3, "medium": 0.5, "hard": 0.2}',
  started_at timestamptz NOT NULL DEFAULT now(),
  submitted_at timestamptz,
  score integer CHECK (score >= 0 AND score <= 100),
  total_questions integer NOT NULL CHECK (total_questions >= 5 AND total_questions <= 30),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create quiz_session_questions table
CREATE TABLE IF NOT EXISTS quiz_session_questions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_session_id uuid NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
  question_id uuid NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  index integer NOT NULL CHECK (index >= 0),
  correct_choice text NOT NULL,
  explanation text NOT NULL,
  selected_choice text,
  is_correct boolean,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(quiz_session_id, question_id),
  UNIQUE(quiz_session_id, index)
);

-- Add indexes for efficient querying on quiz_sessions
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_child_created ON quiz_sessions(child_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_child_status ON quiz_sessions(child_id, status);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status ON quiz_sessions(status);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_subject ON quiz_sessions(subject);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_active ON quiz_sessions(child_id, subject, topic, status)
  WHERE status = 'active';

-- Add indexes for efficient querying on quiz_session_questions
CREATE INDEX IF NOT EXISTS idx_quiz_session_questions_session ON quiz_session_questions(quiz_session_id, index);
CREATE INDEX IF NOT EXISTS idx_quiz_session_questions_question ON quiz_session_questions(question_id);

-- Add trigger to update updated_at timestamp on quiz_sessions
CREATE OR REPLACE FUNCTION update_quiz_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER quiz_sessions_updated_at
  BEFORE UPDATE ON quiz_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_quiz_sessions_updated_at();

-- Add trigger to auto-expire sessions older than 24 hours
CREATE OR REPLACE FUNCTION auto_expire_quiz_sessions()
RETURNS TRIGGER AS $$
BEGIN
  -- Auto-expire active sessions older than 24 hours
  IF NEW.status = 'active' AND NEW.created_at < now() - interval '24 hours' THEN
    NEW.status = 'expired';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_expire_quiz_sessions_trigger
  BEFORE UPDATE ON quiz_sessions
  FOR EACH ROW
  WHEN (OLD.status = 'active' AND NEW.status = 'active')
  EXECUTE FUNCTION auto_expire_quiz_sessions();

-- Add comments for documentation
COMMENT ON TABLE quiz_sessions IS 'Quiz sessions with fixed question sets and timed completion';
COMMENT ON COLUMN quiz_sessions.id IS 'Unique quiz session identifier';
COMMENT ON COLUMN quiz_sessions.child_id IS 'Reference to the child taking the quiz';
COMMENT ON COLUMN quiz_sessions.subject IS 'Subject being tested (Math, Reading, Science, etc.)';
COMMENT ON COLUMN quiz_sessions.topic IS 'Specific topic within the subject';
COMMENT ON COLUMN quiz_sessions.subtopic IS 'Specific subtopic within the topic (optional)';
COMMENT ON COLUMN quiz_sessions.status IS 'Session status: active, completed, or expired';
COMMENT ON COLUMN quiz_sessions.duration_sec IS 'Quiz duration in seconds (300-7200)';
COMMENT ON COLUMN quiz_sessions.difficulty_mix_config IS 'JSON config for difficulty proportions';
COMMENT ON COLUMN quiz_sessions.started_at IS 'Server timestamp when quiz was created';
COMMENT ON COLUMN quiz_sessions.submitted_at IS 'When the quiz was submitted';
COMMENT ON COLUMN quiz_sessions.score IS 'Final score as percentage (0-100)';
COMMENT ON COLUMN quiz_sessions.total_questions IS 'Total number of questions in the quiz';
COMMENT ON COLUMN quiz_sessions.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN quiz_sessions.updated_at IS 'Record last update timestamp';

COMMENT ON TABLE quiz_session_questions IS 'Questions included in a quiz session with correct answers';
COMMENT ON COLUMN quiz_session_questions.id IS 'Unique identifier for this quiz-question association';
COMMENT ON COLUMN quiz_session_questions.quiz_session_id IS 'Reference to the quiz session';
COMMENT ON COLUMN quiz_session_questions.question_id IS 'Reference to the question';
COMMENT ON COLUMN quiz_session_questions.index IS 'Order of question in the quiz (0-based)';
COMMENT ON COLUMN quiz_session_questions.correct_choice IS 'The correct answer choice';
COMMENT ON COLUMN quiz_session_questions.explanation IS 'Explanation of the correct answer';
COMMENT ON COLUMN quiz_session_questions.selected_choice IS 'User's selected answer (NULL if unanswered)';
COMMENT ON COLUMN quiz_session_questions.is_correct IS 'Whether the user answered correctly (NULL before submission)';
COMMENT ON COLUMN quiz_session_questions.created_at IS 'Record creation timestamp';

-- Rollback script (run manually if needed):
/*
DROP TRIGGER IF EXISTS auto_expire_quiz_sessions_trigger ON quiz_sessions;
DROP FUNCTION IF EXISTS auto_expire_quiz_sessions();
DROP TRIGGER IF EXISTS quiz_sessions_updated_at ON quiz_sessions;
DROP FUNCTION IF EXISTS update_quiz_sessions_updated_at();
DROP INDEX IF EXISTS idx_quiz_session_questions_question;
DROP INDEX IF EXISTS idx_quiz_session_questions_session;
DROP INDEX IF EXISTS idx_quiz_sessions_active;
DROP INDEX IF EXISTS idx_quiz_sessions_subject;
DROP INDEX IF EXISTS idx_quiz_sessions_status;
DROP INDEX IF EXISTS idx_quiz_sessions_child_status;
DROP INDEX IF EXISTS idx_quiz_sessions_child_created;
DROP TABLE IF EXISTS quiz_session_questions CASCADE;
DROP TABLE IF EXISTS quiz_sessions CASCADE;
DROP TYPE IF EXISTS quiz_status;
*/
