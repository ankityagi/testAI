# Phase 2: Question Selection with Subtopic Awareness

## Overview
Update the question picker to select questions based on subtopics, ensuring users work through all subtopics systematically before repeating content.

---

## Implementation Steps

### 2.0 Clear Question Bank (NEW)

**Decision:** Start fresh with subtopic-aware question generation.

**Checklist:**
- [ ] Create `scripts/reset_question_bank.sh` script
- [ ] Execute TRUNCATE statements via psql or Python script
- [ ] Verify tables are empty

**Action:**
```sql
-- Clear existing questions (they will be regenerated with proper subtopics)
TRUNCATE TABLE question_bank CASCADE;

-- Also clear related tracking tables
TRUNCATE TABLE attempts CASCADE;
TRUNCATE TABLE seen_questions CASCADE;
```

**Validation:**
```python
# Verify all tables are empty
from studybuddy.backend.db.repository import build_repository
repo = build_repository()
assert repo.count_questions() == 0, "question_bank should be empty"
print("✓ Question bank cleared successfully")
```

**Why this approach:**
- Ensures all questions have proper subtopic references from the start
- Avoids complexity of backfilling/mapping existing questions
- Questions will be regenerated on-demand with subtopic context
- Clean slate for testing the new subtopic-aware system

**Note:** This is acceptable for development. For production with real user data, you would need a migration strategy.

---

### 2.1 Add Subtopic Parameter to Repository Methods

Add `subtopic` parameter to question-related methods in repository protocol and implementations.

**Checklist:**
- [ ] Update `repository.py` Protocol: Add `subtopic: str | None = None` to `list_questions()` signature
- [ ] Update `repository.py` Protocol: Add `subtopic: str | None = None` to `count_questions()` signature
- [ ] Update `postgres_repo.py`: Implement subtopic filtering in `list_questions()` WHERE clause
- [ ] Update `postgres_repo.py`: Implement subtopic filtering in `count_questions()` WHERE clause

**Code Changes:**

**In `repository.py`:**
```python
def list_questions(
    self,
    subject: str,
    grade: int,
    topic: str,
    subtopic: str | None = None,  # NEW
    child_id: str | None = None,
    limit: int | None = None
) -> list[dict]: ...

def count_questions(
    self,
    subject: str | None = None,
    grade: int | None = None,
    topic: str | None = None,
    subtopic: str | None = None,  # NEW
) -> int: ...
```

**In `postgres_repo.py`:**
```python
def list_questions(self, subject, grade, topic, subtopic=None, child_id=None, limit=None):
    # ... existing code ...
    where_clauses = [
        "subject = %s",
        "grade = %s",
        "topic = %s",
    ]
    params = [subject, grade, topic]

    # NEW: Add subtopic filter if provided
    if subtopic is not None:
        where_clauses.append("sub_topic = %s")
        params.append(subtopic)

    # ... rest of query ...
```

**Validation:**
```python
# Test subtopic filtering
from studybuddy.backend.db.repository import build_repository
repo = build_repository()

# After questions are generated, verify filtering works
all_questions = repo.list_questions("math", 3, "addition", subtopic=None)
filtered_questions = repo.list_questions("math", 3, "addition", subtopic="adding within 20")

print(f"Total questions: {len(all_questions)}")
print(f"Filtered questions: {len(filtered_questions)}")
assert len(filtered_questions) <= len(all_questions), "Filtered should be subset"
print("✓ Subtopic filtering works correctly")
```

### 2.2 Create Subtopic Selection Logic

**IMPORTANT:** This auto-selection only happens when the user/frontend does NOT explicitly provide a subtopic.

**Checklist:**
- [ ] Create `select_next_subtopic()` function in `question_picker.py`
- [ ] Query all subtopics for the given subject/grade/topic
- [ ] For each subtopic, count unseen questions for the child
- [ ] Sort by: (1) unseen count DESC, (2) sequence_order ASC
- [ ] Return the top subtopic
- [ ] Handle edge case: no subtopics exist for topic (fallback to None or default)

**Code Implementation:**

**In `question_picker.py`:**
```python
def select_next_subtopic(
    repo: Repository,
    child_id: str,
    subject: str,
    topic: str,
    grade: int
) -> str | None:
    """
    Select the next subtopic for a child to work on.
    Prioritizes subtopics with more unseen questions, then by sequence order.

    Returns None if no subtopics exist for the topic.
    """
    # Get all subtopics for this topic
    subtopics = repo.list_subtopics(subject=subject, grade=grade, topic=topic)

    if not subtopics:
        print(f"[SELECT_SUBTOPIC] No subtopics found for {subject}/{grade}/{topic}")
        return None

    # For each subtopic, count unseen questions
    subtopic_scores = []
    for st in subtopics:
        subtopic_name = st["subtopic"]

        # Count total questions for this subtopic
        total = repo.count_questions(
            subject=subject,
            grade=grade,
            topic=topic,
            subtopic=subtopic_name
        )

        # Count seen questions for this child
        seen = repo.count_seen_questions(
            child_id=child_id,
            subject=subject,
            grade=grade,
            topic=topic,
            subtopic=subtopic_name
        )

        unseen = total - seen

        subtopic_scores.append({
            "subtopic": subtopic_name,
            "unseen": unseen,
            "sequence_order": st.get("sequence_order", 999)
        })

    # Sort by unseen (DESC), then sequence_order (ASC)
    subtopic_scores.sort(key=lambda x: (-x["unseen"], x["sequence_order"]))

    selected = subtopic_scores[0]["subtopic"]
    print(f"[SELECT_SUBTOPIC] Selected: {selected} (unseen: {subtopic_scores[0]['unseen']})")

    return selected
```

**Logic flow:**
```python
# In fetch_batch() or question route
if payload.subtopic:
    # User explicitly selected a subtopic - use it
    subtopic = payload.subtopic
else:
    # No subtopic provided - auto-select intelligently
    subtopic = select_next_subtopic(repo, child_id, subject, topic, grade)
```

This allows:
- **Frontend control:** If the UI lets users pick a specific subtopic, honor that choice
- **Smart defaults:** If no subtopic specified, system automatically selects the best one
- **Flexibility:** Supports both guided learning (auto-select) and free exploration (user-select)

**Validation:**
```python
# Test subtopic selection
from studybuddy.backend.db.repository import build_repository
from studybuddy.backend.services.question_picker import select_next_subtopic

repo = build_repository()

# Test with a real child/subject/topic
selected = select_next_subtopic(
    repo=repo,
    child_id="test-child-id",
    subject="math",
    topic="addition",
    grade=3
)

print(f"Selected subtopic: {selected}")
assert selected is not None, "Should select a subtopic"
assert isinstance(selected, str), "Should return string"
print("✓ Subtopic selection works correctly")
```

### 2.3 Update `fetch_batch()` to Use Subtopics

Modify to select subtopic, query by subtopic, generate for subtopic.

**Checklist:**
- [ ] Update `fetch_batch()` signature to accept `subtopic: str | None` parameter
- [ ] Add conditional logic: if subtopic is None, call `select_next_subtopic()`
- [ ] Pass subtopic to `repo.list_questions()` call
- [ ] Update stock check to use subtopic-specific count
- [ ] Return `selected_subtopic` in QuestionBatch dataclass
- [ ] Update `QuestionBatch` dataclass to include `selected_subtopic: str` field

**Critical Implementation Detail - Stock Deficit Tracking:**

The `fetch_batch()` function must return which specific subtopic needs restocking:

**In `question_picker.py`:**
```python
@dataclass
class QuestionBatch:
    questions: list[dict]
    stock_deficit: int
    selected_subtopic: str  # NEW: Track which subtopic was used

def fetch_batch(
    repo: Repository,
    child: dict,
    subject: str,
    topic: str,
    subtopic: str | None = None,  # NEW: Optional subtopic
    limit: int = 10,
) -> QuestionBatch:
    """Fetch a batch of questions for the child."""
    child_id = child["id"]
    grade = child["grade"]

    # AUTO-SELECT subtopic if not provided
    if subtopic is None:
        subtopic = select_next_subtopic(repo, child_id, subject, topic, grade)
        print(f"[FETCH_BATCH] Auto-selected subtopic: {subtopic}")
    else:
        print(f"[FETCH_BATCH] Using provided subtopic: {subtopic}")

    # Query questions for THIS SPECIFIC subtopic
    available = repo.list_questions(
        subject=subject,
        grade=grade,
        topic=topic,
        subtopic=subtopic,  # Filter by subtopic
        child_id=child_id,
        limit=None  # Get all for selection
    )

    # ... existing question selection logic (adaptive, dedup, etc.) ...
    picked = select_questions_for_child(available, child_id, limit)

    # Check stock level for THIS SPECIFIC subtopic
    stock_level = repo.count_questions(
        subject=subject,
        grade=grade,
        topic=topic,
        subtopic=subtopic,  # The one we just used
    )

    stock_deficit = max(MIN_STOCK_THRESHOLD - stock_level, 0)

    return QuestionBatch(
        questions=picked[:limit],
        stock_deficit=stock_deficit,
        selected_subtopic=subtopic  # CRITICAL: Return the subtopic that needs restocking
    )
```

**Why this matters:**
- Background task needs to know WHICH subtopic to generate for
- Can't just generate random questions - must target the depleted subtopic
- Ensures even distribution of questions across all subtopics

**Validation:**
```python
# Test fetch_batch with subtopic selection
from studybuddy.backend.db.repository import build_repository
from studybuddy.backend.services.question_picker import fetch_batch

repo = build_repository()
child = {"id": "test-child", "grade": 3}

# Test auto-selection (no subtopic provided)
batch = fetch_batch(
    repo=repo,
    child=child,
    subject="math",
    topic="addition",
    subtopic=None,  # Should auto-select
    limit=5
)

print(f"Selected subtopic: {batch.selected_subtopic}")
print(f"Questions returned: {len(batch.questions)}")
print(f"Stock deficit: {batch.stock_deficit}")

assert batch.selected_subtopic is not None, "Should auto-select a subtopic"
assert isinstance(batch.selected_subtopic, str), "Subtopic should be string"
print("✓ fetch_batch with auto-selection works correctly")

# Test explicit subtopic
batch2 = fetch_batch(
    repo=repo,
    child=child,
    subject="math",
    topic="addition",
    subtopic="adding within 20",  # Explicit
    limit=5
)

assert batch2.selected_subtopic == "adding within 20", "Should use provided subtopic"
print("✓ fetch_batch with explicit subtopic works correctly")
```

### 2.4 Update Routes and Models

Update `/fetch` endpoint and API models to support subtopic selection and return.

**Checklist:**
- [ ] Update `QuestionRequest` model in `models.py`: Add `subtopic: str | None = None` field
- [ ] Update `QuestionResponse` model in `models.py`: Add `selected_subtopic: str` field
- [ ] Update `/fetch` endpoint in `routes/questions.py`: Pass subtopic to fetch_batch
- [ ] Update `/fetch` endpoint: Use `batch.selected_subtopic` for background restocking
- [ ] Update `/fetch` endpoint: Return `selected_subtopic` in response

**Code Changes:**

**In `models.py`:**
```python
class QuestionRequest(BaseModel):
    subject: str
    topic: str | None = None
    subtopic: str | None = None  # NEW: Optional subtopic selection
    limit: int = 10

class QuestionResponse(BaseModel):
    questions: list[dict]
    selected_subtopic: str  # NEW: Return which subtopic was used
```

**In `routes/questions.py`:**
```python
@router.post("/fetch")
def fetch_questions(
    payload: QuestionRequest,
    background_tasks: BackgroundTasks,
    auth_user: dict = Depends(get_auth_user)
):
    # ... existing validation ...
    repo = build_repository()
    child = repo.get_child(payload.child_id)

    # Determine topic
    topic = payload.topic or pacing.first_topic_or_default(...)

    # CONDITIONAL subtopic selection
    if payload.subtopic:
        # User provided subtopic explicitly - use it
        subtopic = payload.subtopic
        print(f"[ROUTE] Using user-specified subtopic: {subtopic}")
    else:
        # No subtopic provided - let picker auto-select
        subtopic = None  # picker.fetch_batch will handle selection
        print(f"[ROUTE] No subtopic specified, will auto-select")

    batch = picker.fetch_batch(
        repo=repo,
        child=child,
        subject=payload.subject,
        topic=topic,
        subtopic=subtopic,  # Can be None or user-specified
        limit=payload.limit,
    )

    # CRITICAL: Restock the SPECIFIC subtopic that was used
    if batch.stock_deficit > 0:
        background_tasks.add_task(
            picker.top_up_stock,
            repo=repo,
            child=child,
            subject=payload.subject,
            topic=topic,
            subtopic=batch.selected_subtopic,  # Use the DEPLETED subtopic, not a random one
            count=batch.stock_deficit,
        )

    return QuestionResponse(
        questions=batch.questions,
        selected_subtopic=batch.selected_subtopic  # Always return what was used
    )
```

**Validation:**
```bash
# Start development server
make dev

# Test with curl - auto-selection
curl -X POST http://localhost:8000/questions/fetch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child",
    "subject": "math",
    "topic": "addition",
    "limit": 5
  }'

# Should return:
# {
#   "questions": [...],
#   "selected_subtopic": "adding within 20"  # Auto-selected
# }

# Test with explicit subtopic
curl -X POST http://localhost:8000/questions/fetch \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child",
    "subject": "math",
    "topic": "addition",
    "subtopic": "adding two-digit numbers",
    "limit": 5
  }'

# Should return:
# {
#   "questions": [...],
#   "selected_subtopic": "adding two-digit numbers"  # User-specified
# }
```

---

### 2.5 Update Question Generation with Subtopic Context

Ensure generated questions include subtopic information in prompts and storage.

**Checklist:**
- [ ] Update `GenerationContext` dataclass in `genai.py`: Add `subtopic: str` field
- [ ] Update `_build_prompt()` function: Include subtopic in OpenAI prompt
- [ ] Update `top_up_stock()` function: Accept and pass subtopic parameter
- [ ] Verify generated questions have `sub_topic` field populated

**Code Changes:**

**In `genai.py`:**
```python
@dataclass
class GenerationContext:
    subject: str
    grade: int
    topic: str
    subtopic: str  # NEW: Include subtopic in generation context
    child_id: str | None = None
    difficulty: str = "medium"

def _build_prompt(context: GenerationContext) -> str:
    """Build OpenAI prompt with subtopic context."""
    prompt = f"""Generate a {context.subject} question for grade {context.grade}.

Topic: {context.topic}
Subtopic: {context.subtopic}  # NEW: Include in prompt

The question should:
- Be appropriate for grade {context.grade}
- Focus specifically on: {context.subtopic}
- Align with Common Core or Eureka Math standards
- Be at {context.difficulty} difficulty level
...
"""
    return prompt

def generate_question(context: GenerationContext) -> dict:
    """Generate a single question using OpenAI."""
    prompt = _build_prompt(context)

    # ... OpenAI API call ...

    return {
        "stem": parsed_question["stem"],
        "options": parsed_question["options"],
        "correct_answer": parsed_question["correct_answer"],
        "subject": context.subject,
        "grade": context.grade,
        "topic": context.topic,
        "sub_topic": context.subtopic,  # NEW: Store subtopic
        "difficulty": context.difficulty,
        "question_hash": compute_hash(...)
    }
```

**In `question_picker.py`:**
```python
def top_up_stock(
    repo: Repository,
    child: dict,
    subject: str,
    topic: str,
    subtopic: str,  # NEW: Required parameter
    count: int = 10
) -> None:
    """Generate questions to restock inventory for a SPECIFIC subtopic."""
    print(f"[TOP_UP] Generating {count} questions for {subject}/{topic}/{subtopic}")

    context = GenerationContext(
        subject=subject,
        grade=child["grade"],
        topic=topic,
        subtopic=subtopic,  # NEW: Pass to generation
        child_id=child["id"]
    )

    for i in range(count):
        try:
            question = generate_question(context)
            repo.insert_question(question)
            print(f"[TOP_UP] Generated {i+1}/{count} for subtopic: {subtopic}")
        except Exception as e:
            print(f"[TOP_UP] Error generating question: {e}")
```

**Validation:**
```python
# Test question generation with subtopic
from studybuddy.backend.services.genai import GenerationContext, generate_question
from studybuddy.backend.db.repository import build_repository

context = GenerationContext(
    subject="math",
    grade=3,
    topic="addition",
    subtopic="adding within 20",
    difficulty="easy"
)

question = generate_question(context)

print(f"Generated question: {question['stem']}")
print(f"Subtopic: {question['sub_topic']}")

assert question["sub_topic"] == "adding within 20", "Subtopic should match"
assert question["topic"] == "addition", "Topic should match"
assert question["grade"] == 3, "Grade should match"

print("✓ Question generation with subtopic works correctly")

# Save to database and verify
repo = build_repository()
repo.insert_question(question)

# Query back
questions = repo.list_questions(
    subject="math",
    grade=3,
    topic="addition",
    subtopic="adding within 20"
)

assert len(questions) > 0, "Should find generated question"
assert any(q["sub_topic"] == "adding within 20" for q in questions), "Should have correct subtopic"
print("✓ Question storage and retrieval with subtopic works correctly")
```

---

## Expected Outcomes

1. Questions selected per-subtopic
2. Users progress through subtopics systematically
3. Frontend receives `selected_subtopic`
4. No more `topic=None` queries
5. **Background restocking targets the specific depleted subtopic** (not random generation)
6. All generated questions have proper `sub_topic` values
7. OpenAI prompts include subtopic context for better targeted questions

---

### 2.6 End-to-End Integration Testing

Test the complete flow from API request to question delivery with subtopics.

**Checklist:**
- [ ] Clear question bank and verify empty state
- [ ] Create test child account
- [ ] Make API request without subtopic (test auto-selection)
- [ ] Verify questions are generated for selected subtopic
- [ ] Make API request with explicit subtopic
- [ ] Verify correct subtopic is used
- [ ] Verify background restocking targets correct subtopic
- [ ] Test multiple requests exhaust one subtopic and move to next

**Integration Test Script:**

Create `scripts/test_subtopic_flow.py`:
```python
#!/usr/bin/env python3
"""
End-to-end test for subtopic-aware question flow.
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_subtopic_flow():
    print("=== Phase 2 Integration Test ===\n")

    # 1. Setup: Create test user and child
    print("[1] Creating test user and child...")
    signup_resp = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    })
    assert signup_resp.status_code == 200
    token = signup_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    child_resp = requests.post(f"{BASE_URL}/children", headers=headers, json={
        "name": "Test Child",
        "grade": 3
    })
    assert child_resp.status_code == 200
    child_id = child_resp.json()["id"]
    print(f"   ✓ Created child: {child_id}")

    # 2. Test auto-selection (no subtopic provided)
    print("\n[2] Testing auto-selection (no subtopic)...")
    fetch_resp = requests.post(f"{BASE_URL}/questions/fetch", headers=headers, json={
        "child_id": child_id,
        "subject": "math",
        "topic": "addition",
        "limit": 5
    })
    assert fetch_resp.status_code == 200
    data = fetch_resp.json()

    assert "selected_subtopic" in data, "Response should include selected_subtopic"
    assert len(data["questions"]) > 0, "Should return questions"

    auto_selected = data["selected_subtopic"]
    print(f"   ✓ Auto-selected subtopic: {auto_selected}")
    print(f"   ✓ Returned {len(data['questions'])} questions")

    # Verify all questions have correct subtopic
    for q in data["questions"]:
        assert q["sub_topic"] == auto_selected, f"Question subtopic mismatch"
    print(f"   ✓ All questions match subtopic: {auto_selected}")

    # 3. Test explicit subtopic selection
    print("\n[3] Testing explicit subtopic selection...")
    fetch_resp2 = requests.post(f"{BASE_URL}/questions/fetch", headers=headers, json={
        "child_id": child_id,
        "subject": "math",
        "topic": "addition",
        "subtopic": "adding two-digit numbers",
        "limit": 5
    })
    assert fetch_resp2.status_code == 200
    data2 = fetch_resp2.json()

    assert data2["selected_subtopic"] == "adding two-digit numbers"
    print(f"   ✓ Used explicit subtopic: {data2['selected_subtopic']}")

    # 4. Verify background generation happened
    print("\n[4] Waiting for background generation...")
    time.sleep(5)  # Give background task time to complete

    # Request again - should have more stock now
    fetch_resp3 = requests.post(f"{BASE_URL}/questions/fetch", headers=headers, json={
        "child_id": child_id,
        "subject": "math",
        "topic": "addition",
        "subtopic": auto_selected,
        "limit": 5
    })
    assert fetch_resp3.status_code == 200
    print(f"   ✓ Background generation completed")

    print("\n=== All Integration Tests Passed ✓ ===")

if __name__ == "__main__":
    test_subtopic_flow()
```

**Run Test:**
```bash
# Terminal 1: Start server
make dev

# Terminal 2: Run integration test
python3 scripts/test_subtopic_flow.py
```

---

## Files to Modify

1. `studybuddy/backend/db/repository.py` - Add subtopic parameters
2. `studybuddy/backend/db/postgres_repo.py` - Implement subtopic filtering
3. `studybuddy/backend/services/question_picker.py` - Add selection logic
4. `studybuddy/backend/services/genai.py` - Ensure subtopic in generation
5. `studybuddy/backend/routes/questions.py` - Update endpoint
6. `studybuddy/backend/models.py` - Update models

---

## Quick Start Script

Create `scripts/reset_question_bank.sh`:
```bash
#!/bin/bash
# Reset question bank for subtopic implementation
set -a
source .env
set +a

echo "⚠️  WARNING: This will delete ALL questions, attempts, and seen_questions!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" == "yes" ]; then
    echo "Truncating tables..."
    # Add SQL execution here
    echo "✓ Question bank reset complete"
    echo "Questions will be regenerated with subtopics on-demand"
else
    echo "Cancelled"
fi
```

---

**Estimated Time: 2 days** (no backfill needed)
