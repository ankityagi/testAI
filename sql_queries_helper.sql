-- SQL Queries Helper
-- Manual queries for inspecting question picker behavior and data on Supabase
-- Copy and paste these queries into Supabase SQL Editor

-- ============================================================================
-- SECTION 1: QUESTION INVENTORY QUERIES
-- ============================================================================

-- 1. Count total questions by subject
SELECT
    subject,
    COUNT(*) as total_questions,
    COUNT(DISTINCT topic) as unique_topics,
    COUNT(DISTINCT sub_topic) as unique_subtopics
FROM question_bank
WHERE source IS NULL OR source != 'mock'
GROUP BY subject
ORDER BY subject;

-- 2. Count questions by subject, topic, and subtopic
SELECT
    subject,
    topic,
    sub_topic as subtopic,
    difficulty,
    COUNT(*) as question_count
FROM question_bank
WHERE source IS NULL OR source != 'mock'
GROUP BY subject, topic, sub_topic, difficulty
ORDER BY subject, topic, sub_topic, difficulty;

-- 3. Find subtopics with low question counts (less than 5)
SELECT
    subject,
    topic,
    sub_topic as subtopic,
    difficulty,
    COUNT(*) as question_count
FROM question_bank
WHERE source IS NULL OR source != 'mock'
GROUP BY subject, topic, sub_topic, difficulty
HAVING COUNT(*) < 5
ORDER BY question_count ASC, subject, topic, sub_topic;

-- 4. Check for questions without subtopics
SELECT
    subject,
    topic,
    sub_topic,
    COUNT(*) as count
FROM question_bank
WHERE (sub_topic IS NULL OR sub_topic = '')
  AND (source IS NULL OR source != 'mock')
GROUP BY subject, topic, sub_topic
ORDER BY count DESC;

-- ============================================================================
-- SECTION 2: SUBTOPICS TABLE QUERIES
-- ============================================================================

-- 5. List all subtopics with their sequence order
SELECT
    subject,
    grade,
    topic,
    subtopic,
    description,
    sequence_order
FROM subtopics
ORDER BY subject, grade, topic, sequence_order, subtopic;

-- 6. Count subtopics by subject and grade
SELECT
    subject,
    grade,
    COUNT(*) as subtopic_count
FROM subtopics
GROUP BY subject, grade
ORDER BY subject, grade;

-- 7. Find subtopics with no matching questions
SELECT
    s.subject,
    s.grade,
    s.topic,
    s.subtopic
FROM subtopics s
LEFT JOIN question_bank q ON
    s.subject = q.subject
    AND s.topic = q.topic
    AND s.subtopic = q.sub_topic
    AND (q.source IS NULL OR q.source != 'mock')
WHERE q.id IS NULL
ORDER BY s.subject, s.grade, s.topic, s.subtopic;

-- ============================================================================
-- SECTION 3: CHILD PERFORMANCE QUERIES
-- ============================================================================

-- 8. Get child's attempt history with question details
-- Replace 'CHILD_ID_HERE' with actual child UUID
SELECT
    a.created_at,
    a.correct,
    a.time_spent_ms,
    q.subject,
    q.topic,
    q.sub_topic as subtopic,
    q.difficulty,
    q.stem
FROM attempts a
JOIN question_bank q ON a.question_id = q.id
WHERE a.child_id = 'CHILD_ID_HERE'
ORDER BY a.created_at DESC
LIMIT 50;

-- 9. Calculate child's accuracy by subtopic
-- Replace 'CHILD_ID_HERE' with actual child UUID
SELECT
    q.subject,
    q.topic,
    q.sub_topic as subtopic,
    COUNT(*) as attempts,
    SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) as correct_answers,
    ROUND(100.0 * SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_percent,
    AVG(a.time_spent_ms) as avg_time_ms
FROM attempts a
JOIN question_bank q ON a.question_id = q.id
WHERE a.child_id = 'CHILD_ID_HERE'
GROUP BY q.subject, q.topic, q.sub_topic
ORDER BY attempts DESC, accuracy_percent ASC;

-- 10. Get child's current streak
-- Replace 'CHILD_ID_HERE' with actual child UUID
WITH ordered_attempts AS (
    SELECT
        correct,
        ROW_NUMBER() OVER (ORDER BY created_at DESC) as rn
    FROM attempts
    WHERE child_id = 'CHILD_ID_HERE'
)
SELECT
    COUNT(*) as current_streak
FROM ordered_attempts
WHERE rn <= (
    SELECT MIN(rn) - 1
    FROM ordered_attempts
    WHERE NOT correct
);

-- 11. Get child's seen questions (for deduplication)
-- Replace 'CHILD_ID_HERE' with actual child UUID
SELECT
    sq.question_hash,
    q.subject,
    q.topic,
    q.sub_topic as subtopic,
    q.stem
FROM seen_questions sq
JOIN question_bank q ON sq.question_hash = q.hash
WHERE sq.child_id = 'CHILD_ID_HERE'
ORDER BY q.subject, q.topic, q.sub_topic;

-- ============================================================================
-- SECTION 4: SESSION TRACKING QUERIES
-- ============================================================================

-- 12. Get all sessions for a child
-- Replace 'CHILD_ID_HERE' with actual child UUID
SELECT
    id,
    child_id,
    subject,
    topic,
    subtopic,
    started_at,
    ended_at,
    EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at)) * 1000 as duration_ms,
    created_at
FROM sessions
WHERE child_id = 'CHILD_ID_HERE'
ORDER BY started_at DESC;

-- 13. Get active sessions (not ended)
SELECT
    s.id,
    s.child_id,
    c.name as child_name,
    s.subject,
    s.topic,
    s.subtopic,
    s.started_at,
    EXTRACT(EPOCH FROM (NOW() - s.started_at)) * 1000 as duration_ms
FROM sessions s
JOIN children c ON s.child_id = c.id
WHERE s.ended_at IS NULL
ORDER BY s.started_at DESC;

-- 14. Get session summary with attempts
-- Replace 'SESSION_ID_HERE' with actual session UUID
WITH session_attempts AS (
    SELECT
        a.*,
        q.subject,
        q.topic,
        q.sub_topic as subtopic
    FROM attempts a
    JOIN question_bank q ON a.question_id = q.id
    WHERE a.child_id = (SELECT child_id FROM sessions WHERE id = 'SESSION_ID_HERE')
      AND a.created_at >= (SELECT started_at FROM sessions WHERE id = 'SESSION_ID_HERE')
      AND a.created_at <= COALESCE(
          (SELECT ended_at FROM sessions WHERE id = 'SESSION_ID_HERE'),
          NOW()
      )
)
SELECT
    COUNT(*) as questions_attempted,
    SUM(CASE WHEN correct THEN 1 ELSE 0 END) as questions_correct,
    ROUND(100.0 * SUM(CASE WHEN correct THEN 1 ELSE 0 END) / COUNT(*), 0) as accuracy,
    SUM(time_spent_ms) as total_time_ms,
    AVG(time_spent_ms) as avg_time_per_question_ms,
    STRING_AGG(DISTINCT subject, ', ') as subjects_practiced
FROM session_attempts;

-- ============================================================================
-- SECTION 5: ADAPTIVE DIFFICULTY QUERIES
-- ============================================================================

-- 15. Get subtopic performance for adaptive difficulty calculation
-- Replace 'CHILD_ID_HERE' and 'SUBTOPIC_NAME' with actual values
SELECT
    q.difficulty,
    COUNT(*) as attempts,
    SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) as correct_answers,
    ROUND(100.0 * SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_percent
FROM attempts a
JOIN question_bank q ON a.question_id = q.id
WHERE a.child_id = 'CHILD_ID_HERE'
  AND q.sub_topic = 'SUBTOPIC_NAME'
GROUP BY q.difficulty
ORDER BY
    CASE q.difficulty
        WHEN 'easy' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'hard' THEN 3
    END;

-- 16. Check recent streak performance (last 5 attempts)
-- Replace 'CHILD_ID_HERE' with actual child UUID
SELECT
    a.created_at,
    a.correct,
    q.subject,
    q.topic,
    q.sub_topic as subtopic,
    q.difficulty
FROM attempts a
JOIN question_bank q ON a.question_id = q.id
WHERE a.child_id = 'CHILD_ID_HERE'
ORDER BY a.created_at DESC
LIMIT 5;

-- ============================================================================
-- SECTION 6: QUESTION SELECTION SIMULATION
-- ============================================================================

-- 17. Simulate question selection for a subtopic
-- Replace parameters: CHILD_ID, SUBJECT, TOPIC, SUBTOPIC, DIFFICULTY
-- This shows questions that WOULD be selected (excluding seen questions)
SELECT
    q.id,
    q.subject,
    q.topic,
    q.sub_topic as subtopic,
    q.difficulty,
    q.stem,
    q.hash
FROM question_bank q
WHERE q.subject = 'math'  -- Replace
  AND q.topic = 'multiplication'  -- Replace
  AND q.sub_topic = 'Single-Digit Multiplication'  -- Replace
  AND q.difficulty = 'easy'  -- Replace or use IN ('easy', 'medium')
  AND (q.source IS NULL OR q.source != 'mock')
  AND q.hash NOT IN (
      SELECT question_hash
      FROM seen_questions
      WHERE child_id = 'CHILD_ID_HERE'  -- Replace
  )
ORDER BY RANDOM()
LIMIT 5;

-- 18. Count available questions per difficulty (excluding seen)
-- Replace CHILD_ID, SUBJECT, TOPIC, SUBTOPIC
SELECT
    q.difficulty,
    COUNT(*) as available_questions
FROM question_bank q
WHERE q.subject = 'math'  -- Replace
  AND q.topic = 'multiplication'  -- Replace
  AND q.sub_topic = 'Single-Digit Multiplication'  -- Replace
  AND (q.source IS NULL OR q.source != 'mock')
  AND q.hash NOT IN (
      SELECT question_hash
      FROM seen_questions
      WHERE child_id = 'CHILD_ID_HERE'  -- Replace
  )
GROUP BY q.difficulty
ORDER BY
    CASE q.difficulty
        WHEN 'easy' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'hard' THEN 3
    END;

-- ============================================================================
-- SECTION 7: DATA INTEGRITY CHECKS
-- ============================================================================

-- 19. Find duplicate question hashes
SELECT
    hash,
    COUNT(*) as count,
    STRING_AGG(DISTINCT subject || '/' || topic || '/' || sub_topic, ', ') as locations
FROM question_bank
GROUP BY hash
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 20. Check for orphaned attempts (question not found)
SELECT
    a.id as attempt_id,
    a.child_id,
    a.question_id,
    a.created_at
FROM attempts a
LEFT JOIN question_bank q ON a.question_id = q.id
WHERE q.id IS NULL
ORDER BY a.created_at DESC;

-- 21. Check for orphaned seen_questions
SELECT
    sq.child_id,
    sq.question_hash,
    COUNT(*) as count
FROM seen_questions sq
LEFT JOIN question_bank q ON sq.question_hash = q.hash
WHERE q.id IS NULL
GROUP BY sq.child_id, sq.question_hash
ORDER BY count DESC;

-- ============================================================================
-- SECTION 8: PERFORMANCE METRICS
-- ============================================================================

-- 22. Get overall platform statistics
SELECT
    (SELECT COUNT(*) FROM parents) as total_parents,
    (SELECT COUNT(*) FROM children) as total_children,
    (SELECT COUNT(*) FROM question_bank WHERE source IS NULL OR source != 'mock') as total_questions,
    (SELECT COUNT(*) FROM attempts) as total_attempts,
    (SELECT COUNT(*) FROM sessions) as total_sessions,
    (SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL) as active_sessions;

-- 23. Get busiest hours for attempts
SELECT
    EXTRACT(HOUR FROM created_at) as hour,
    COUNT(*) as attempts_count
FROM attempts
GROUP BY EXTRACT(HOUR FROM created_at)
ORDER BY hour;

-- 24. Get average session duration
SELECT
    AVG(EXTRACT(EPOCH FROM (ended_at - started_at)) * 1000) as avg_duration_ms,
    MIN(EXTRACT(EPOCH FROM (ended_at - started_at)) * 1000) as min_duration_ms,
    MAX(EXTRACT(EPOCH FROM (ended_at - started_at)) * 1000) as max_duration_ms
FROM sessions
WHERE ended_at IS NOT NULL;

-- ============================================================================
-- SECTION 9: DEBUGGING SPECIFIC ISSUES
-- ============================================================================

-- 25. Find sessions without any attempts
SELECT
    s.id,
    s.child_id,
    s.subject,
    s.topic,
    s.subtopic,
    s.started_at,
    s.ended_at
FROM sessions s
LEFT JOIN attempts a ON
    s.child_id = a.child_id
    AND a.created_at >= s.started_at
    AND (s.ended_at IS NULL OR a.created_at <= s.ended_at)
WHERE a.id IS NULL
ORDER BY s.started_at DESC;

-- 26. Check question distribution across difficulties
SELECT
    subject,
    difficulty,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY subject), 1) as percentage
FROM question_bank
WHERE source IS NULL OR source != 'mock'
GROUP BY subject, difficulty
ORDER BY subject,
    CASE difficulty
        WHEN 'easy' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'hard' THEN 3
    END;

-- 27. Find children with unusual attempt patterns
SELECT
    child_id,
    COUNT(*) as total_attempts,
    AVG(time_spent_ms) as avg_time_ms,
    SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct_count,
    ROUND(100.0 * SUM(CASE WHEN correct THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy
FROM attempts
GROUP BY child_id
HAVING AVG(time_spent_ms) < 1000 OR AVG(time_spent_ms) > 300000  -- Less than 1s or more than 5min
ORDER BY avg_time_ms DESC;

-- ============================================================================
-- SECTION 10: USEFUL VIEWS FOR ANALYSIS
-- ============================================================================

-- 28. Create a view for child performance summary (run once to create view)
-- DROP VIEW IF EXISTS child_performance_summary;
-- CREATE VIEW child_performance_summary AS
-- SELECT
--     c.id as child_id,
--     c.name as child_name,
--     c.grade,
--     COUNT(a.id) as total_attempts,
--     SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) as correct_answers,
--     ROUND(100.0 * SUM(CASE WHEN a.correct THEN 1 ELSE 0 END) / COUNT(a.id), 1) as accuracy,
--     AVG(a.time_spent_ms) as avg_time_ms,
--     COUNT(DISTINCT q.subject) as subjects_practiced,
--     COUNT(DISTINCT s.id) as sessions_completed
-- FROM children c
-- LEFT JOIN attempts a ON c.id = a.child_id
-- LEFT JOIN question_bank q ON a.question_id = q.id
-- LEFT JOIN sessions s ON c.id = s.child_id AND s.ended_at IS NOT NULL
-- GROUP BY c.id, c.name, c.grade;

-- Query the view (after creating it)
-- SELECT * FROM child_performance_summary ORDER BY total_attempts DESC;

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- Tips for using these queries:
--
-- 1. Replace placeholder values:
--    - CHILD_ID_HERE: Use actual UUID from children table
--    - SESSION_ID_HERE: Use actual UUID from sessions table
--    - Subject/topic/subtopic: Use actual values from your data
--
-- 2. Finding UUIDs:
--    SELECT id, name FROM children;
--    SELECT id, started_at FROM sessions ORDER BY started_at DESC LIMIT 10;
--
-- 3. Performance:
--    - Add LIMIT clauses when exploring large datasets
--    - Check execution plans with EXPLAIN ANALYZE for slow queries
--
-- 4. Common filters:
--    - Exclude mock data: WHERE source IS NULL OR source != 'mock'
--    - Recent data only: WHERE created_at > NOW() - INTERVAL '7 days'
--    - Specific parent: WHERE parent_id = 'PARENT_UUID'
--
-- 5. Useful aggregations:
--    - Accuracy: ROUND(100.0 * SUM(CASE WHEN correct THEN 1 ELSE 0 END) / COUNT(*), 1)
--    - Time format: EXTRACT(EPOCH FROM duration) * 1000 for milliseconds
--    - Percentages: Use window functions with OVER (PARTITION BY ...)
