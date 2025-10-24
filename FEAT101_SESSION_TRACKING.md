# FEAT-101: Session Tracking Implementation

## Status: ✅ Backend MVP Complete (October 19, 2025)

## Overview
Implemented automatic session tracking for practice sessions, enabling session analytics and insights.

## Implementation Summary

### 1. Database Schema ✅
**File**: `studybuddy/backend/db/sql/migration_add_sessions.sql`

Created `sessions` table with:
- `id` (UUID, primary key)
- `child_id` (UUID, foreign key to children)
- `subject`, `topic`, `subtopic` (text, nullable)
- `started_at` (timestamptz, default now())
- `ended_at` (timestamptz, nullable - NULL means active session)
- `created_at`, `updated_at` (timestamptz)

**Indexes created**:
- `idx_sessions_child_started` - for querying by child and time range
- `idx_sessions_child_ended` - for ended sessions
- `idx_sessions_subject` - for filtering by subject
- `idx_sessions_active` - for finding active sessions (WHERE ended_at IS NULL)

**Migration applied**: ✅ Successfully applied to Supabase PostgreSQL

### 2. Backend Models ✅
**File**: `studybuddy/backend/models.py`

Added Pydantic models:
```python
class Session(BaseModel):
    id: str
    child_id: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class SessionSummary(BaseModel):
    session: Session
    questions_attempted: int
    questions_correct: int
    accuracy: int  # Percentage 0-100
    total_time_ms: int
    avg_time_per_question_ms: int
    subjects_practiced: list[str]
```

Updated `QuestionResponse` to include `session_id`:
```python
class QuestionResponse(BaseModel):
    questions: list[Question]
    selected_subtopic: Optional[str] = None
    session_id: Optional[str] = None  # NEW
```

### 3. Repository Methods ✅
**Files**:
- `studybuddy/backend/db/repository.py` (Protocol)
- `studybuddy/backend/db/postgres_repo.py` (Implementation)

Added methods:
- `create_session()` - Create new practice session
- `get_active_session()` - Get active (not ended) session for a child
- `get_session()` - Get session by ID
- `end_session()` - End session by setting ended_at timestamp
- `get_session_summary()` - Calculate session statistics (attempts, accuracy, time)

### 4. Auto Session Tracking ✅
**File**: `studybuddy/backend/routes/questions.py`

Modified `/questions/fetch` endpoint to:
1. Check for active session using `repo.get_active_session(child_id)`
2. If no active session, create one with `repo.create_session()`
3. Return `session_id` in response for frontend tracking

**Logic**:
```python
# Get or create active session
active_session = repo.get_active_session(payload.child_id)
if not active_session:
    active_session = repo.create_session(
        child_id=payload.child_id,
        subject=payload.subject,
        topic=topic,
        subtopic=batch.selected_subtopic,
    )
```

### 5. Session API Endpoints ✅
**File**: `studybuddy/backend/routes/sessions.py`

Created new router with 3 endpoints:

#### GET /sessions/{session_id}
- Returns session details
- Validates parent has access to session's child

#### GET /sessions/{session_id}/summary
- Returns session summary with statistics:
  - Questions attempted/correct
  - Accuracy percentage
  - Total time and average time per question
  - Subjects practiced
- Validates parent access
- Calculates stats from attempts within session time window

#### POST /sessions/{session_id}/end
- Ends a practice session (sets `ended_at = now()`)
- Validates parent access
- Returns updated session

**Router registered** in `studybuddy/backend/app.py`:
```python
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
```

## API Usage Examples

### 1. Fetching Questions (Auto Session Creation)
```bash
POST /questions/fetch
{
  "child_id": "...",
  "subject": "Math",
  "topic": "Multiplication",
  "limit": 5
}

Response:
{
  "questions": [...],
  "selected_subtopic": "Single-Digit Multiplication",
  "session_id": "abc123..."  # <-- NEW: Session ID returned
}
```

### 2. Get Session Summary
```bash
GET /sessions/{session_id}/summary
Authorization: Bearer {token}

Response:
{
  "session": {
    "id": "abc123...",
    "child_id": "...",
    "subject": "Math",
    "topic": "Multiplication",
    "subtopic": "Single-Digit Multiplication",
    "started_at": "2025-10-19T10:00:00Z",
    "ended_at": null,
    "created_at": "2025-10-19T10:00:00Z",
    "updated_at": "2025-10-19T10:00:00Z"
  },
  "questions_attempted": 10,
  "questions_correct": 8,
  "accuracy": 80,
  "total_time_ms": 300000,
  "avg_time_per_question_ms": 30000,
  "subjects_practiced": ["Math"]
}
```

### 3. End Session
```bash
POST /sessions/{session_id}/end
Authorization: Bearer {token}

Response:
{
  "id": "abc123...",
  "child_id": "...",
  "subject": "Math",
  "topic": "Multiplication",
  "subtopic": "Single-Digit Multiplication",
  "started_at": "2025-10-19T10:00:00Z",
  "ended_at": "2025-10-19T10:15:00Z",  # <-- Now populated
  "created_at": "2025-10-19T10:00:00Z",
  "updated_at": "2025-10-19T10:15:00Z"
}
```

## Key Features

### ✅ Automatic Session Management
- Session automatically created on first question fetch
- Reuses active session for subsequent fetches
- No manual session creation required by frontend

### ✅ Session Context Tracking
- Captures subject/topic/subtopic of practice session
- Tracks session duration (started_at → ended_at)
- Links all attempts within time window

### ✅ Session Analytics
- Questions attempted and correct count
- Accuracy percentage (integer 0-100)
- Total time spent and average per question
- List of subjects practiced

### ✅ Security
- All endpoints validate parent access to child
- Session IDs are UUIDs (secure, non-guessable)
- Authorization required for all operations

## Database Queries

### Find Active Session for Child
```sql
SELECT * FROM sessions
WHERE child_id = $1 AND ended_at IS NULL
ORDER BY started_at DESC
LIMIT 1
```

### Get Session Summary
```sql
-- Get attempts within session window
SELECT a.*, q.subject
FROM attempts a
JOIN question_bank q ON a.question_id = q.id
WHERE a.child_id = $1
  AND a.created_at >= $2  -- started_at
  AND a.created_at <= $3  -- ended_at (or now() if still active)
ORDER BY a.created_at
```

## Files Created/Modified

### Created
1. `studybuddy/backend/db/sql/migration_add_sessions.sql`
2. `studybuddy/backend/routes/sessions.py`
3. `scripts/apply_sessions_migration.py`
4. `scripts/run_sessions_migration.sh`

### Modified
1. `studybuddy/backend/models.py` - Added Session, SessionSummary models
2. `studybuddy/backend/db/repository.py` - Added session method signatures
3. `studybuddy/backend/db/postgres_repo.py` - Implemented session methods
4. `studybuddy/backend/routes/questions.py` - Added auto session tracking
5. `studybuddy/backend/app.py` - Registered sessions router

## Next Steps (Frontend Integration)

### Required Frontend Changes
1. **Store session_id** from `/questions/fetch` response
2. **"End Session" Button** - Call `POST /sessions/{id}/end`
3. **Session Summary Page** - Display stats from `GET /sessions/{id}/summary`
4. **Session History** - List past sessions (needs new endpoint)

### Recommended UI Flow
```
User starts practice
  ↓
Frontend calls /questions/fetch
  ↓
Backend creates session, returns session_id
  ↓
Frontend stores session_id in component state
  ↓
User answers questions (attempts logged)
  ↓
User clicks "End Session" button
  ↓
Frontend calls POST /sessions/{session_id}/end
  ↓
Frontend navigates to session summary page
  ↓
Display stats from GET /sessions/{session_id}/summary
```

## Testing

### Manual Testing
```bash
# 1. Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.access_token')

# 2. Fetch questions (creates session)
SESSION_ID=$(curl -s -X POST http://localhost:8000/questions/fetch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"...","subject":"Math","limit":5}' \
  | jq -r '.session_id')

# 3. Get session summary
curl -X GET http://localhost:8000/sessions/$SESSION_ID/summary \
  -H "Authorization: Bearer $TOKEN"

# 4. End session
curl -X POST http://localhost:8000/sessions/$SESSION_ID/end \
  -H "Authorization: Bearer $TOKEN"
```

## Performance Considerations

### Indexes
All critical queries are indexed:
- Active session lookup: O(log n) using `idx_sessions_active`
- Session by child: O(log n) using `idx_sessions_child_started`
- Subject filtering: O(log n) using `idx_sessions_subject`

### Query Optimization
- Session summary aggregates data in single query
- Uses JOIN to minimize database round trips
- Efficient time window filtering with indexed timestamps

## Future Enhancements (FEAT-102)

1. **Session History Endpoint** - `GET /sessions?child_id=...&limit=10`
2. **Multi-Session Analytics** - Compare sessions over time
3. **Session Trends** - Accuracy/speed improvement over time
4. **Auto-End Sessions** - Close inactive sessions after timeout (e.g., 30 min)
5. **Session Pause/Resume** - Allow pausing and resuming sessions

## Conclusion

✅ **FEAT-101 Backend MVP Complete**
- Database schema designed and migrated
- Auto session tracking implemented
- Session management endpoints created
- Ready for frontend integration

**Status**: Backend implementation complete, awaiting frontend integration.
