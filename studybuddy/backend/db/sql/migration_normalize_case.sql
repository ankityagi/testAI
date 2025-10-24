-- Migration: Normalize case for subject/topic/subtopic fields
-- Purpose: Convert all existing metadata to lowercase for consistent querying
-- Date: 2025-10-22
--
-- This migration normalizes metadata fields (subject, topic, subtopic) to lowercase
-- across all tables while preserving question content (stem, options, answers) as-is.

-- ============================================================================
-- QUESTION_BANK TABLE
-- ============================================================================

-- Update question_bank: normalize subject, topic, sub_topic to lowercase
UPDATE question_bank
SET
    subject = LOWER(subject),
    topic = LOWER(topic),
    sub_topic = LOWER(sub_topic)
WHERE
    subject != LOWER(subject)
    OR topic != LOWER(topic)
    OR sub_topic != LOWER(sub_topic);

-- Verify question_bank normalization
SELECT
    COUNT(*) as total_questions,
    COUNT(CASE WHEN subject ~ '[A-Z]' THEN 1 END) as uppercase_subjects,
    COUNT(CASE WHEN topic ~ '[A-Z]' THEN 1 END) as uppercase_topics,
    COUNT(CASE WHEN sub_topic ~ '[A-Z]' THEN 1 END) as uppercase_subtopics
FROM question_bank;

-- Expected result: uppercase_subjects, uppercase_topics, uppercase_subtopics should all be 0

-- ============================================================================
-- SUBTOPICS TABLE
-- ============================================================================

-- Update subtopics: normalize subject, topic, subtopic to lowercase
UPDATE subtopics
SET
    subject = LOWER(subject),
    topic = LOWER(topic),
    subtopic = LOWER(subtopic)
WHERE
    subject != LOWER(subject)
    OR topic != LOWER(topic)
    OR subtopic != LOWER(subtopic);

-- Verify subtopics normalization
SELECT
    COUNT(*) as total_subtopics,
    COUNT(CASE WHEN subject ~ '[A-Z]' THEN 1 END) as uppercase_subjects,
    COUNT(CASE WHEN topic ~ '[A-Z]' THEN 1 END) as uppercase_topics,
    COUNT(CASE WHEN subtopic ~ '[A-Z]' THEN 1 END) as uppercase_subtopics
FROM subtopics;

-- Expected result: uppercase_subjects, uppercase_topics, uppercase_subtopics should all be 0

-- ============================================================================
-- SESSIONS TABLE
-- ============================================================================

-- Update sessions: normalize subject, topic, subtopic to lowercase
UPDATE sessions
SET
    subject = LOWER(subject),
    topic = LOWER(topic),
    subtopic = LOWER(subtopic)
WHERE
    (subject IS NOT NULL AND subject != LOWER(subject))
    OR (topic IS NOT NULL AND topic != LOWER(topic))
    OR (subtopic IS NOT NULL AND subtopic != LOWER(subtopic));

-- Verify sessions normalization
SELECT
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN subject ~ '[A-Z]' THEN 1 END) as uppercase_subjects,
    COUNT(CASE WHEN topic ~ '[A-Z]' THEN 1 END) as uppercase_topics,
    COUNT(CASE WHEN subtopic ~ '[A-Z]' THEN 1 END) as uppercase_subtopics
FROM sessions;

-- Expected result: uppercase_subjects, uppercase_topics, uppercase_subtopics should all be 0

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Show sample of normalized data
SELECT
    'question_bank' as table_name,
    subject,
    topic,
    sub_topic as subtopic,
    COUNT(*) as count
FROM question_bank
GROUP BY subject, topic, sub_topic
ORDER BY subject, topic, sub_topic
LIMIT 10;

SELECT
    'subtopics' as table_name,
    subject,
    topic,
    subtopic,
    COUNT(*) as count
FROM subtopics
GROUP BY subject, topic, subtopic
ORDER BY subject, topic, subtopic
LIMIT 10;

SELECT
    'sessions' as table_name,
    subject,
    topic,
    subtopic,
    COUNT(*) as count
FROM sessions
WHERE subject IS NOT NULL
GROUP BY subject, topic, subtopic
ORDER BY subject, topic, subtopic
LIMIT 10;

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- 1. This migration is IDEMPOTENT - safe to run multiple times
-- 2. Only metadata fields are normalized (subject, topic, subtopic)
-- 3. Question content (stem, options, correct_answer) remains unchanged
-- 4. After running, all queries should use lowercase metadata
-- 5. Display layer should format metadata as Title Case for users
--
-- To verify success:
-- - All uppercase counts should be 0
-- - All metadata should be lowercase
-- - Question content should preserve original case
--
-- To rollback (NOT RECOMMENDED):
-- This migration cannot be easily rolled back as original case is lost.
-- Instead, rely on display formatting to show proper case to users.
