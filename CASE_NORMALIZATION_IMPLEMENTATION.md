# Case Normalization Implementation

**Date:** October 24, 2025
**Status:** ✅ IMPLEMENTED - Migration Pending

## Problem Statement

OpenAI generates questions with capitalized metadata (e.g., `subject="Math"`, `topic="Multiplication"`), but the question picker queries with lowercase values (e.g., `subject="math"`, `topic="multiplication"`), causing query mismatches and preventing questions from being found.

## Solution Overview

Implemented a **3-layer normalization strategy**:

1. **Storage Layer** - Normalize metadata to lowercase when storing
2. **Query Layer** - Normalize inputs to lowercase before querying
3. **Display Layer** - Format metadata as Title Case for users

**Key Principle:** Metadata (subject/topic/subtopic) is normalized, but question content (stem, options, answers) preserves original case for correctness.

---

## Implementation Details

### 1. Text Utilities (`studybuddy/backend/services/text_utils.py`)

**New File Created** - Provides normalization and formatting functions:

```python
def normalize_subject(subject: str) -> str
def normalize_topic(topic: str) -> str
def normalize_subtopic(subtopic: str) -> str
def to_display_case(text: str) -> str
def normalize_metadata(data: dict) -> dict
```

**Purpose:**
- Convert metadata to lowercase for storage and queries
- Format metadata as Title Case for API responses
- Preserve question content case sensitivity

---

### 2. Database Layer Updates (`studybuddy/backend/db/postgres_repo.py`)

#### Insertion Methods (Normalize Before Storing)

**`insert_questions()`** - Lines 333-376
```python
from ..services.text_utils import normalize_metadata

# Normalize metadata (subject, topic, subtopic) to lowercase
normalize_metadata(payload)
```

**`insert_subtopics()`** - Lines 507-544
```python
# Normalize metadata before insertion
normalized = {**subtopic}
normalize_metadata(normalized)
```

**`create_session()`** - Lines 612-641
```python
# Normalize metadata before insertion
normalized_subject = normalize_subject(subject) if subject else None
normalized_topic = normalize_topic(topic) if topic else None
normalized_subtopic = normalize_subtopic(subtopic) if subtopic else None
```

#### Query Methods (Normalize Inputs)

**`list_questions()`** - Lines 239-298
```python
from ..services.text_utils import normalize_subject, normalize_topic, normalize_subtopic

# Normalize inputs before querying
params = [normalize_subject(subject)]
params.append(normalize_topic(topic))
params.append(normalize_subtopic(subtopic))
```

**`count_questions()`** - Lines 300-337
```python
# Normalize inputs before querying
params = [normalize_subject(subject)]
```

**`list_subtopics()`** - Lines 546-574
```python
# Normalize inputs before querying
params = [normalize_subject(subject)]
params.append(normalize_topic(topic))
```

**`count_subtopics()`** - Lines 587-609
```python
# Normalize inputs before querying
params = [normalize_subject(subject)]
params.append(normalize_topic(topic))
```

---

### 3. API Routes Updates (Display Formatting)

#### Questions Routes (`studybuddy/backend/routes/questions.py`)

**`GET /questions/topics`** - Lines 14-35
```python
from ..services.text_utils import to_display_case

# Format for display (Title Case)
topics.append({"topic": to_display_case(topic)})
```

**`GET /questions/subtopics`** - Lines 38-58
```python
# Format metadata for display (Title Case)
for st in subtopics:
    if "subject" in st:
        st["subject"] = to_display_case(st["subject"])
    if "topic" in st:
        st["topic"] = to_display_case(st["topic"])
    if "subtopic" in st:
        st["subtopic"] = to_display_case(st["subtopic"])
```

**`POST /questions/fetch`** - Lines 61-129
```python
return QuestionResponse(
    questions=batch.questions,
    selected_subtopic=to_display_case(batch.selected_subtopic) if batch.selected_subtopic else None,
    session_id=active_session.get("id")
)
```

#### Session Routes (`studybuddy/backend/routes/sessions.py`)

**`GET /sessions/{session_id}`** - Lines 12-36
```python
from ..services.text_utils import to_display_case

# Format metadata for display
if session_data.get("subject"):
    session_data["subject"] = to_display_case(session_data["subject"])
if session_data.get("topic"):
    session_data["topic"] = to_display_case(session_data["topic"])
if session_data.get("subtopic"):
    session_data["subtopic"] = to_display_case(session_data["subtopic"])
```

**`GET /sessions/{session_id}/summary`** - Lines 39-68
```python
# Format session metadata for display
if "session" in summary_data and summary_data["session"]:
    session = summary_data["session"]
    if session.get("subject"):
        session["subject"] = to_display_case(session["subject"])
    if session.get("topic"):
        session["topic"] = to_display_case(session["topic"])
    if session.get("subtopic"):
        session["subtopic"] = to_display_case(session["subtopic"])
```

**`POST /sessions/{session_id}/end`** - Lines 71-101
```python
# Format metadata for display
if ended_session.get("subject"):
    ended_session["subject"] = to_display_case(ended_session["subject"])
if ended_session.get("topic"):
    ended_session["topic"] = to_display_case(ended_session["topic"])
if ended_session.get("subtopic"):
    ended_session["subtopic"] = to_display_case(ended_session["subtopic"])
```

---

### 4. Database Migration

#### Migration SQL (`studybuddy/backend/db/sql/migration_normalize_case.sql`)

**Purpose:** Normalize existing data in database

**Tables Updated:**
- `question_bank` - Normalizes `subject`, `topic`, `sub_topic`
- `subtopics` - Normalizes `subject`, `topic`, `subtopic`
- `sessions` - Normalizes `subject`, `topic`, `subtopic`

**SQL Operations:**
```sql
UPDATE question_bank
SET
    subject = LOWER(subject),
    topic = LOWER(topic),
    sub_topic = LOWER(sub_topic)
WHERE
    subject != LOWER(subject)
    OR topic != LOWER(topic)
    OR sub_topic != LOWER(sub_topic);
```

**Verification Queries:**
- Counts uppercase instances (should be 0 after migration)
- Shows sample normalized data
- Validates all metadata is lowercase

#### Migration Script (`scripts/run_normalize_migration.sh`)

**Features:**
- Loads environment variables
- Connects to Supabase database
- Prompts for confirmation before running
- Executes migration SQL
- Provides next steps guidance

**Usage:**
```bash
source .env && ./scripts/run_normalize_migration.sh
```

---

### 5. Test Suite (`scripts/test_normalization.py`)

**Test Coverage:**

1. **Normalization Functions Test**
   - Tests `normalize_subject()`, `normalize_topic()`, `normalize_subtopic()`
   - Verifies lowercase conversion
   - Tests `to_display_case()` Title Case formatting

2. **Metadata Normalization Test**
   - Tests `normalize_metadata()` on dictionaries
   - Verifies metadata fields are normalized
   - Confirms question content is unchanged

3. **Case Preservation Test**
   - Verifies stem, options, answers preserve original case
   - Tests with case-sensitive answers (e.g., "Na" vs "na", "Hola" vs "hola")

4. **Query Matching Test**
   - Simulates queries with different cases
   - Verifies all match after normalization
   - Tests display formatting consistency

**Test Results:**
```
✅ ALL TESTS PASSED

Summary:
  ✓ Subject/topic/subtopic normalized to lowercase for storage
  ✓ Queries normalize input before comparing
  ✓ Display formatting converts to Title Case
  ✓ Question content (stem, options, answers) preserved as-is
```

---

## Behavior Examples

### Example 1: OpenAI Question Generation

**OpenAI Output:**
```json
{
  "subject": "Math",
  "topic": "Multiplication",
  "sub_topic": "Single-Digit Multiplication",
  "stem": "What is 2 × 3?",
  "options": ["5", "6", "7", "8"],
  "correct_answer": "6"
}
```

**After `insert_questions()`:**
```json
{
  "subject": "math",
  "topic": "multiplication",
  "sub_topic": "single-digit multiplication",
  "stem": "What is 2 × 3?",
  "options": ["5", "6", "7", "8"],
  "correct_answer": "6"
}
```

**API Response (GET /questions/fetch):**
```json
{
  "selected_subtopic": "Single-Digit Multiplication",
  "questions": [...]
}
```

### Example 2: Query Matching

**User Query (Any Case):**
```python
list_questions(
    subject="MATH",  # or "Math" or "math"
    topic="Multiplication",
    subtopic="Single-Digit Multiplication"
)
```

**Normalized Query:**
```python
list_questions(
    subject="math",
    topic="multiplication",
    subtopic="single-digit multiplication"
)
```

**Result:** ✅ Matches stored data regardless of input case

### Example 3: Case-Sensitive Answers

**Question:**
```json
{
  "stem": "What is the chemical symbol for Sodium?",
  "options": ["Na", "na", "NA", "nA"],
  "correct_answer": "Na"
}
```

**Behavior:**
- Metadata normalized: `subject="science"`, `topic="chemistry"`
- Answer comparison: Case-sensitive `selected == "Na"`
- User selecting "na" → ❌ Incorrect
- User selecting "Na" → ✅ Correct

---

## Files Modified

### New Files Created
1. `studybuddy/backend/services/text_utils.py` - Normalization utilities
2. `studybuddy/backend/db/sql/migration_normalize_case.sql` - Migration SQL
3. `scripts/run_normalize_migration.sh` - Migration runner script
4. `scripts/test_normalization.py` - Test suite
5. `CASE_NORMALIZATION_IMPLEMENTATION.md` - This document

### Existing Files Modified
1. `studybuddy/backend/db/postgres_repo.py` - Database layer normalization
2. `studybuddy/backend/routes/questions.py` - Display formatting
3. `studybuddy/backend/routes/sessions.py` - Display formatting

---

## Testing Strategy

### Unit Tests (Completed)
- ✅ Normalization functions
- ✅ Metadata normalization
- ✅ Case preservation
- ✅ Query matching

### Integration Tests (Manual)
1. **Generate questions via OpenAI** with capitalized metadata
2. **Verify storage** - Check database has lowercase metadata
3. **Query questions** - Use mixed case inputs
4. **Verify retrieval** - Questions found regardless of case
5. **Check API responses** - Metadata formatted as Title Case
6. **Test answer validation** - Case-sensitive comparison works

### Database Migration Tests
1. **Before migration** - Count uppercase instances
2. **Run migration** - Execute normalization SQL
3. **After migration** - Verify all metadata is lowercase
4. **Query validation** - Test queries work correctly

---

## Rollout Plan

### Phase 1: Code Deployment ✅ COMPLETED
- [x] Implement text_utils.py
- [x] Update database layer (postgres_repo.py)
- [x] Update API routes (questions.py, sessions.py)
- [x] Create test suite
- [x] Verify tests pass

### Phase 2: Database Migration ⏳ PENDING
- [ ] Backup database (Supabase automatic backups)
- [ ] Run migration: `source .env && ./scripts/run_normalize_migration.sh`
- [ ] Verify migration succeeded (uppercase counts = 0)
- [ ] Test question picker with existing data

### Phase 3: Validation ⏳ PENDING
- [ ] Generate new questions via OpenAI
- [ ] Verify they are found by picker
- [ ] Test UI displays Title Case correctly
- [ ] Monitor logs for any case-related errors

---

## Rollback Plan

**If issues occur:**

1. **Code rollback** - Revert commits:
   ```bash
   git revert <commit-hash>
   ```

2. **Database rollback** - NOT RECOMMENDED
   - Original case is lost after migration
   - Instead, rely on display formatting to show proper case
   - Future questions will have correct case from OpenAI

3. **Mitigation** - Fix display issues in frontend:
   - API already returns Title Case
   - Ensure frontend uses API values as-is

---

## Performance Impact

**Negligible:**
- `normalize_*()` functions are simple string operations (`.lower().strip()`)
- Called once per insertion/query, not in hot loops
- Display formatting only affects API responses (minimal data)

**Database:**
- No new indexes required
- Queries remain efficient (exact matches)
- Migration is one-time operation

---

## Security Considerations

**No security impact:**
- Normalization is case-folding, not sanitization
- Input validation remains unchanged
- SQL injection prevention unchanged
- Authentication/authorization unchanged

---

## Future Enhancements

1. **Make case-sensitivity configurable per question type**
   ```python
   # Add field to question schema
   case_sensitive: bool = True

   # Modify answer comparison
   if question.get("case_sensitive", True):
       correct = selected == correct_answer
   else:
       correct = selected.lower() == correct_answer.lower()
   ```

2. **Add database constraints**
   ```sql
   -- Ensure metadata is always lowercase
   ALTER TABLE question_bank ADD CONSTRAINT subject_lowercase
       CHECK (subject = LOWER(subject));
   ```

3. **Add migration tracking**
   ```sql
   CREATE TABLE migrations (
       id SERIAL PRIMARY KEY,
       name TEXT NOT NULL,
       executed_at TIMESTAMP DEFAULT NOW()
   );
   ```

---

## Related Documentation

- [CASE_SENSITIVITY_VALIDATION.md](./CASE_SENSITIVITY_VALIDATION.md) - Original case sensitivity validation
- [sql_queries_helper.sql](./sql_queries_helper.sql) - SQL queries for inspection
- [FEAT-101-SESSION-INSIGHTS.md](./FEAT-101-SESSION-INSIGHTS.md) - Session tracking feature

---

## Summary

**Problem:** OpenAI capitalized metadata vs. lowercase queries = no matches
**Solution:** 3-layer normalization (storage, query, display)
**Status:** Code complete, tests passing, migration script ready
**Next Step:** Run database migration on Supabase

**Impact:**
- ✅ Questions always found regardless of case
- ✅ Consistent UI display (Title Case)
- ✅ Preserves answer case sensitivity
- ✅ Zero breaking changes

