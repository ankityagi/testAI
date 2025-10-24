-- Migration: Add sessions table for practice session tracking (FEAT-101)
-- Description: Tracks practice sessions for session insights and analytics
-- Created: 2025-10-19

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  child_id uuid NOT NULL REFERENCES children(id) ON DELETE CASCADE,
  subject text,
  topic text,
  subtopic text,
  started_at timestamptz NOT NULL DEFAULT now(),
  ended_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Add indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_sessions_child_started ON sessions(child_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_child_ended ON sessions(child_id, ended_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_subject ON sessions(subject);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(child_id, ended_at) WHERE ended_at IS NULL;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sessions_updated_at
  BEFORE UPDATE ON sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_sessions_updated_at();

-- Add comment for documentation
COMMENT ON TABLE sessions IS 'Practice sessions for tracking student learning time and progress';
COMMENT ON COLUMN sessions.id IS 'Unique session identifier';
COMMENT ON COLUMN sessions.child_id IS 'Reference to the child who owns this session';
COMMENT ON COLUMN sessions.subject IS 'Subject being studied (Math, Reading, Science, etc.)';
COMMENT ON COLUMN sessions.topic IS 'Specific topic within the subject';
COMMENT ON COLUMN sessions.subtopic IS 'Specific subtopic within the topic';
COMMENT ON COLUMN sessions.started_at IS 'When the session started';
COMMENT ON COLUMN sessions.ended_at IS 'When the session ended (NULL if still active)';
COMMENT ON COLUMN sessions.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN sessions.updated_at IS 'Record last update timestamp';
