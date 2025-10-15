# Subtopic Management Implementation Plan

## Overview
Implement a comprehensive subtopic management system that:
1. **Pre-generates all subtopics** for grades K-12 using a one-time seed script with OpenAI
2. Stores subtopics in the database as static seed data (like current question seeds)
3. Manages question inventory per subtopic per user
4. Ensures users receive questions across all subtopics systematically
5. Uses subtopics in OpenAI prompts when generating new questions to fill the question bank

**Key Design Decision:** Subtopics are **static seed data**, not dynamically generated per child. This approach:
- Ensures consistency across all users
- Reduces OpenAI API calls
- Makes curriculum predictable and reviewable
- Allows manual curation and editing if needed

---

## Database Schema Changes

### New Table: `subtopics`
```sql
CREATE TABLE subtopics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject VARCHAR(50) NOT NULL,
    grade INTEGER NOT NULL,
    topic VARCHAR(200) NOT NULL,
    subtopic VARCHAR(200) NOT NULL,
    description TEXT,
    sequence_order INTEGER,  -- For ordered progression through subtopics
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(subject, grade, topic, subtopic)
);

CREATE INDEX idx_subtopics_lookup ON subtopics(subject, grade, topic);
```

### Modify Table: `question_bank`
Already has `sub_topic` column - ensure it's properly indexed:
```sql
CREATE INDEX IF NOT EXISTS idx_question_bank_subtopic
ON question_bank(subject, grade, topic, sub_topic);
```

### Modify Table: `seen_questions`
Currently tracks by `question_hash`. This remains the same but we'll query differently.

### New Table: `child_subtopic_progress` (Optional - for tracking progression)
```sql
CREATE TABLE child_subtopic_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id UUID REFERENCES children(id) ON DELETE CASCADE,
    subtopic_id UUID REFERENCES subtopics(id) ON DELETE CASCADE,
    questions_seen INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    last_seen_at TIMESTAMP,
    mastery_level VARCHAR(20) DEFAULT 'not_started',  -- not_started, learning, practicing, mastered
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(child_id, subtopic_id)
);

CREATE INDEX idx_child_subtopic_progress ON child_subtopic_progress(child_id, subtopic_id);
```

---

## Implementation Steps

### Phase 1: One-Time Subtopic Seed Generation

#### 1.1 Create Subtopic Generator Script (`scripts/generate_subtopic_seeds.py`)
This is a **one-time script** (similar to how you'd generate `seed_questions.json`) that calls OpenAI to generate all subtopics for K-12.

```python
#!/usr/bin/env python3
"""
One-time script to generate subtopic seed data for all grades K-12.
Run this once to create studybuddy/backend/db/sql/seed_subtopics.json
"""
import json
import os
from typing import Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuration
GRADES = list(range(0, 13))  # K-12 (0 = Kindergarten)
SUBJECTS = ["math", "reading"]

# Topic definitions per grade/subject
# You can expand this based on your pacing.json or standards
TOPICS_BY_GRADE_SUBJECT = {
    "math": {
        0: ["counting", "shapes", "patterns"],
        1: ["addition", "subtraction", "place value", "measurement"],
        2: ["addition", "subtraction", "place value", "time", "money"],
        3: ["multiplication", "division", "fractions", "geometry"],
        # ... continue for all grades
    },
    "reading": {
        0: ["phonics", "sight words", "comprehension"],
        1: ["phonics", "comprehension", "retell", "vocabulary"],
        2: ["fluency", "comprehension", "inference", "vocabulary"],
        # ... continue for all grades
    }
}


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def generate_subtopics_for_topic(
    grade: int,
    subject: str,
    topic: str
) -> list[dict[str, Any]]:
    """Generate subtopics for a specific grade/subject/topic using OpenAI."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    grade_text = f"Kindergarten" if grade == 0 else f"Grade {grade}"

    prompt = f"""For {grade_text} {subject}, generate a comprehensive list of subtopics for the topic "{topic}".

Each subtopic should:
- Be aligned with Common Core or relevant educational standards
- Be specific and measurable
- Follow a logical learning progression from simple to complex
- Include a brief description (1-2 sentences) explaining what students will learn

Respond with a JSON object in this exact format:
{{
  "subtopics": [
    {{
      "subtopic": "name of subtopic",
      "description": "what students will learn in 1-2 sentences",
      "sequence_order": 1
    }}
  ]
}}

Generate 5-10 subtopics per topic, ordered from foundational concepts to advanced applications."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert curriculum designer creating Common Core-aligned subtopics for K-12 education."
            },
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    data = json.loads(response.choices[0].message.content)
    subtopics = data.get("subtopics", [])

    # Add metadata
    for st in subtopics:
        st["subject"] = subject
        st["grade"] = grade
        st["topic"] = topic

    return subtopics


def main():
    """Generate all subtopics and save to seed file."""
    all_subtopics = []

    for subject in SUBJECTS:
        print(f"\n=== Generating subtopics for {subject.upper()} ===")

        for grade in GRADES:
            topics = TOPICS_BY_GRADE_SUBJECT.get(subject, {}).get(grade, [])

            if not topics:
                print(f"  Skipping grade {grade} (no topics defined)")
                continue

            print(f"\n  Grade {grade}:")

            for topic in topics:
                print(f"    - {topic}... ", end="", flush=True)
                try:
                    subtopics = generate_subtopics_for_topic(grade, subject, topic)
                    all_subtopics.extend(subtopics)
                    print(f"✓ ({len(subtopics)} subtopics)")
                except Exception as e:
                    print(f"✗ Error: {e}")

    # Save to seed file
    output_path = "studybuddy/backend/db/sql/seed_subtopics.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_subtopics, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Generated {len(all_subtopics)} subtopics")
    print(f"✓ Saved to {output_path}")
    print(f"\nNext steps:")
    print(f"1. Review the generated subtopics in {output_path}")
    print(f"2. Edit/curate as needed")
    print(f"3. Run database seed script to populate subtopics table")


if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# Set OpenAI key
export OPENAI_API_KEY=sk-...

# Run the generator (takes ~5-10 minutes)
python3 scripts/generate_subtopic_seeds.py

# This creates: studybuddy/backend/db/sql/seed_subtopics.json
```

#### 1.2 Create Database Seed Script for Subtopics
Add to your existing seed logic (`db/sql/seed.sql` or similar):

```sql
-- Load subtopics from seed_subtopics.json
-- This runs once during initial database setup
COPY subtopics (subject, grade, topic, subtopic, description, sequence_order)
FROM '/path/to/seed_subtopics.json'
WITH (FORMAT json);
```

Or add a Python function in `db/seed.py`:
```python
def seed_subtopics(repo: Repository):
    """Load subtopics from seed file into database."""
    seed_file = Path(__file__).parent / "sql" / "seed_subtopics.json"

    if not seed_file.exists():
        print("No seed_subtopics.json found. Run scripts/generate_subtopic_seeds.py first.")
        return

    with seed_file.open("r", encoding="utf-8") as f:
        subtopics = json.load(f)

    repo.insert_subtopics(subtopics)
    print(f"✓ Seeded {len(subtopics)} subtopics")
```

#### 1.3 Repository Methods for Subtopics
Add to `Repository` protocol and implementations:
```python
- insert_subtopics(subtopics: list[dict]) -> None
- list_subtopics(subject: str, grade: int, topic: str) -> list[dict]
- get_subtopic(subtopic_id: str) -> dict | None
- count_questions_by_subtopic(subject: str, grade: int, topic: str, subtopic: str) -> int
```

**No child registration hook needed** - subtopics are pre-seeded during database initialization!

---

### Phase 2: Question Selection with Subtopic Awareness

#### 2.1 Modify `question_picker.py::fetch_batch()`

**Current Flow:**
1. Get child's attempts to determine difficulty
2. Query questions by subject/topic/grade/difficulty
3. Exclude seen questions
4. Generate more if deficit

**New Flow:**
1. Get child's attempts to determine difficulty
2. **Select next subtopic for this child** (new logic)
3. Query questions by subject/topic/**subtopic**/grade/difficulty
4. Exclude seen questions for this subtopic
5. Generate more if deficit **for this specific subtopic**

**New Function:**
```python
def select_next_subtopic(
    repo: Repository,
    child_id: str,
    subject: str,
    topic: str,
    grade: int
) -> str:
    """
    Select the next subtopic for the child based on:
    1. Sequence order (follow curriculum progression)
    2. Unseen question availability
    3. Mastery level (if tracking)

    Strategy:
    - Get all subtopics for topic ordered by sequence_order
    - For each subtopic, check how many unseen questions remain
    - Prefer subtopics with more unseen questions
    - Ensure we cycle through all subtopics before repeating
    """
    subtopics = repo.list_subtopics(subject, grade, topic)

    # Get seen question hashes for this child
    seen_hashes = set(repo.list_seen_question_hashes(child_id))

    # Score each subtopic
    subtopic_scores = []
    for st in subtopics:
        # Count available questions for this subtopic
        all_questions = repo.list_questions(
            subject=subject,
            topic=topic,
            grade=grade,
            subtopic=st["subtopic"]  # NEW PARAMETER
        )
        unseen_count = sum(1 for q in all_questions if q["hash"] not in seen_hashes)

        subtopic_scores.append({
            "subtopic": st["subtopic"],
            "sequence_order": st["sequence_order"],
            "unseen_count": unseen_count
        })

    # Sort by: unseen_count DESC, then sequence_order ASC
    subtopic_scores.sort(key=lambda x: (-x["unseen_count"], x["sequence_order"]))

    # Return subtopic with most unseen questions (ties broken by sequence)
    if subtopic_scores:
        return subtopic_scores[0]["subtopic"]

    # Fallback: return first subtopic
    return subtopics[0]["subtopic"] if subtopics else None
```

#### 2.2 Update Repository `list_questions()` signature
Add optional `subtopic` parameter:
```python
def list_questions(
    self,
    *,
    subject: str,
    topic: str | None = None,
    subtopic: str | None = None,  # NEW
    grade: int | None = None,
    difficulties: Iterable[str] | None = None,
    exclude_hashes: Iterable[str] | None = None,
) -> list[dict]:
```

---

### Phase 3: Question Generation with Subtopics

#### 3.1 Modify `genai.py::GenerationContext`
```python
@dataclass
class GenerationContext:
    subject: str
    topic: str | None
    subtopic: str | None  # NEW
    grade: int | None
    difficulty: str
    count: int
```

#### 3.2 Update `_build_prompt()` to include subtopic
```python
def _build_prompt(ctx: GenerationContext) -> str:
    topic_text = ctx.topic or "grade-level concept"
    subtopic_text = f" specifically focusing on {ctx.subtopic}" if ctx.subtopic else ""
    grade_text = f"Grade {ctx.grade}" if ctx.grade is not None else "Elementary"

    return (
        f"Generate {ctx.count} multiple-choice questions for {grade_text} students "
        f"learning {ctx.subject}. Focus on {topic_text}{subtopic_text}. "
        f"Each question must include exactly four answer options, "
        f"one marked correct, a short rationale, a Common Core style topic tag, "
        f"and a difficulty of {ctx.difficulty}. "
        f"Respond with JSON array where each item has keys: stem, options (array of four strings), "
        f"correct_answer, rationale, subject, grade, topic, sub_topic, difficulty."
    )
```

#### 3.3 Update `question_picker.py::fetch_batch()`
Pass subtopic to generation context:
```python
# Select subtopic
subtopic = select_next_subtopic(repo, child_id, subject, topic, grade)

# Query with subtopic
fetched = repo.list_questions(
    subject=subject,
    topic=topic,
    subtopic=subtopic,  # NEW
    grade=grade,
    difficulties=[difficulty],
    exclude_hashes=seen_hashes,
)

# Generate with subtopic if deficit
if deficit > 0:
    ctx = GenerationContext(
        subject=subject,
        topic=topic,
        subtopic=subtopic,  # NEW
        grade=grade,
        difficulty=preferred_difficulty,
        count=deficit,
    )
```

---

### Phase 4: Stock Management per Subtopic

#### 4.1 Update `MIN_STOCK_THRESHOLD` Logic
Instead of checking stock per topic, check per **subtopic**:

```python
def fetch_batch(...) -> QuestionBatch:
    # ... existing logic ...

    # Check stock level PER SUBTOPIC
    stock_level = repo.count_questions(
        subject=subject,
        topic=topic,
        subtopic=subtopic,  # NEW
        grade=grade
    )

    stock_deficit = max(MIN_STOCK_THRESHOLD - stock_level, 0)
    return QuestionBatch(questions=picked[:limit], stock_deficit=stock_deficit)
```

#### 4.2 Update `top_up_stock()` to accept subtopic
```python
def top_up_stock(
    *,
    repo,
    child: dict,
    subject: str,
    topic: str | None,
    subtopic: str | None,  # NEW
    count: int,
    generator=generate_mcqs,
) -> None:
    grade = child.get("grade")
    ctx = GenerationContext(
        subject=subject,
        topic=topic,
        subtopic=subtopic,  # NEW
        grade=grade,
        difficulty="medium",
        count=count,
    )
    generated = generator(context=ctx)
    # ... rest of function
```

---

### Phase 5: API Updates

#### 5.1 Update `models.py`
```python
class QuestionRequest(BaseModel):
    child_id: str
    subject: str
    topic: str | None = None
    subtopic: str | None = None  # NEW - optional, will be auto-selected if not provided
    limit: int = Field(default=5, ge=1, le=20)

class QuestionResponse(BaseModel):
    questions: list[dict]
    selected_subtopic: str | None = None  # NEW - inform frontend which subtopic was used
```

#### 5.2 Update `routes/questions.py::fetch_questions()`
```python
@router.post("/fetch", response_model=QuestionResponse)
def fetch_questions(
    payload: QuestionRequest,
    background_tasks: BackgroundTasks,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuestionResponse:
    # ... existing validation ...

    # Determine topic (existing logic)
    topic = payload.topic or pacing.first_topic_or_default(...)

    # NEW: Determine subtopic
    if payload.subtopic:
        subtopic = payload.subtopic  # User specified
    else:
        # Auto-select based on child's progress
        subtopic = picker.select_next_subtopic(
            repo=repo,
            child_id=payload.child_id,
            subject=payload.subject,
            topic=topic,
            grade=child["grade"]
        )

    batch = picker.fetch_batch(
        repo=repo,
        child=child,
        subject=payload.subject,
        topic=topic,
        subtopic=subtopic,  # NEW
        limit=payload.limit,
    )

    if batch.stock_deficit > 0:
        background_tasks.add_task(
            picker.top_up_stock,
            repo=repo,
            child=child,
            subject=payload.subject,
            topic=topic,
            subtopic=subtopic,  # NEW
            count=batch.stock_deficit,
        )

    return QuestionResponse(
        questions=batch.questions,
        selected_subtopic=subtopic  # NEW
    )
```

---

### Phase 6: Admin Endpoints for Subtopic Management

#### 6.1 New Route: `/admin/subtopics/list`
```python
@router.get("/admin/subtopics/list")
def list_subtopics(
    subject: str,
    grade: int | None = None,
    topic: str | None = None,
    repo: Repository = Depends(deps.get_repository),
) -> dict:
    """List all subtopics for inspection."""
    subtopics = repo.list_subtopics(subject, grade, topic)
    return {"subtopics": subtopics, "count": len(subtopics)}
```

---

### Phase 7: Frontend Integration Points

#### 7.1 Subtopic Display
Frontend should display which subtopic the user is currently practicing:
```json
{
  "subject": "math",
  "topic": "addition",
  "subtopic": "adding within 20",
  "progress": {
    "questions_in_subtopic": 25,
    "questions_seen": 8,
    "questions_remaining": 17
  }
}
```

#### 7.2 Subtopic Selection UI (Optional)
Allow users to manually select subtopics if desired:
```
GET /api/subtopics?subject=math&grade=3&topic=addition
Response:
{
  "subtopics": [
    {
      "subtopic": "adding within 20",
      "description": "...",
      "progress": {...}
    }
  ]
}
```

---

## Migration Strategy

### Step 1: Generate Subtopic Seed Data (One-Time)
```bash
# Run the subtopic generation script
python3 scripts/generate_subtopic_seeds.py

# This creates: studybuddy/backend/db/sql/seed_subtopics.json
# Review and manually curate if needed
```

### Step 2: Database Migration
```sql
-- Run migration to add subtopics table
CREATE TABLE subtopics (...);

-- Load seed data
-- Use your existing seed mechanism (e.g., Python script or SQL COPY)

-- Backfill existing questions with generic subtopics
UPDATE question_bank
SET sub_topic = topic
WHERE sub_topic IS NULL OR sub_topic = '';
```

### Step 3: Gradual Rollout
1. Deploy new code with subtopic support
2. Existing children continue working (uses fallback logic)
3. New questions use subtopic-aware generation
4. Gradually backfill sub_topic field in existing questions

---

## Testing Strategy

### Unit Tests
1. `test_subtopic_seed_generation.py` - Test seed script functionality (can mock OpenAI)
2. `test_subtopic_selection.py` - Test selection algorithm
3. `test_question_picker_with_subtopics.py` - Test updated picker logic

### Integration Tests
1. Test subtopic seed data loads correctly into database
2. Test question fetching selects appropriate subtopics
3. Test question generation includes subtopic in prompt
4. Test stock management per subtopic

### Manual Testing Checklist
- [ ] Run seed script, verify seed_subtopics.json is created with valid data
- [ ] Load subtopics into database, verify all records inserted
- [ ] Fetch questions, verify subtopic is selected and returned
- [ ] Answer questions, verify progress tracked per subtopic
- [ ] Exhaust questions in one subtopic, verify switches to next
- [ ] Generate questions with low stock, verify subtopic included in prompt

---

## Configuration & Environment Variables

```bash
# Existing
OPENAI_API_KEY=...  # Required for seed script AND question generation
OPENAI_MODEL=gpt-4o-mini

# New
MIN_STOCK_PER_SUBTOPIC=10  # Minimum questions per subtopic
MAX_SUBTOPICS_PER_TOPIC=10  # Limit OpenAI response size in seed script
```

---

## Rollback Plan

If issues arise:
1. Deploy code that makes subtopic parameter optional (with null fallback)
2. Old question picker logic falls back to topic-only queries
3. Database changes are additive (no data loss)
4. Subtopic seed data remains in database for future use

---

## Performance Considerations

### Caching
- Cache subtopics by grade/subject/topic (rarely change)
- Cache subtopic selection per child per session

### Indexing
- Ensure indexes on `question_bank(subject, grade, topic, sub_topic)`
- Index on `subtopics(subject, grade, topic)`

### OpenAI Rate Limits
- Seed script runs once offline (not a concern for production)
- Implement retry logic with exponential backoff in seed script
- Seed script includes delays between API calls to respect rate limits

---

## Future Enhancements

1. **Adaptive Subtopic Sequencing**
   - Use ML to determine optimal subtopic order per child
   - Skip mastered subtopics automatically

2. **Subtopic Mastery Badges**
   - Award badges when child masters a subtopic (e.g., 90% accuracy)

3. **Parent Dashboard**
   - Show subtopic-level progress to parents
   - Highlight struggling subtopics

4. **Teacher Mode**
   - Allow teachers to create custom subtopics
   - Override AI-generated subtopic sequences

---

## Estimated Implementation Time

- Phase 1 (Subtopic Seed Generation Script): 1 day
  - Write script
  - Run script to generate seed_subtopics.json
  - Review and curate output
- Phase 2 (Question Selection): 2 days
- Phase 3 (Question Generation): 1 day
- Phase 4 (Stock Management): 1 day
- Phase 5 (API Updates): 1 day
- Phase 6 (Admin Endpoints): 0.5 day
- Phase 7 (Testing & Polish): 2 days

**Total: ~8-9 days** for complete implementation and testing

**Advantages of Static Seed Approach:**
- Faster implementation (no child registration hooks needed)
- More predictable and reviewable curriculum
- Lower ongoing OpenAI costs
- Easier to version control and audit changes
