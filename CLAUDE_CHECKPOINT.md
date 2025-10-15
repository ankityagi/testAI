# CLAUDE CHECKPOINT

**Date**: October 12, 2025
**Session Context**: Implementing subtopic-based question generation and management system

## Current Problem / Goal 🎯

**Original Issue**: Question generation happening every time user requests questions, regardless of question bank inventory. Also, `topic=None` queries were failing because picker was looking for questions with NULL topic.

**Solution Being Implemented**:
1. Pre-generate static subtopics for all K-12 grades (math & reading)
2. Store subtopics in database as seed data
3. Update question picker to select questions by subtopic
4. Only generate new questions when subtopic inventory is low (< MIN_STOCK_THRESHOLD)
5. Include subtopic in OpenAI prompts for more targeted question generation

## What We Accomplished ✅

### Phase 1: Subtopic Seed Generation (COMPLETED)
- ✅ Created `scripts/generate_subtopic_seeds.py` - OpenAI-powered subtopic generator
- ✅ Generated **1,275 subtopics** across K-12:
  - 648 math subtopics
  - 627 reading subtopics
- ✅ Saved to `studybuddy/backend/db/sql/seed_subtopics.json` (405KB)
- ✅ Updated database schema with `subtopics` table and indexes
- ✅ Implemented repository methods:
  - `insert_subtopics()` - Idempotent inserts
  - `list_subtopics()` - Query with filters
  - `get_subtopic()` - Get by ID
  - `count_subtopics()` - Count with filters
- ✅ Applied migration to add subtopics table to database
- ✅ Loaded all 1,275 subtopics into Supabase

### Planning Documents Created
- ✅ `CLAUDE_PLAN.md` - Full original implementation plan (static seed approach)
- ✅ `CLAUDE_PLAN2.md` - Concise Phase 2 plan (question selection with subtopics)

## Current State 📍

### Environment
- Using hosted Supabase (not local)
- Direct PostgreSQL connection via `psycopg2`
- Remote database: `aws-1-us-west-1.pooler.supabase.com`
- Development server ready on port 8000

### Database State
- ✅ `subtopics` table exists with 1,275 records
- ✅ `question_bank` table has `sub_topic` column (already exists)
- ⚠️ Existing questions in question_bank may have NULL or generic sub_topic values
- **Decision**: Will TRUNCATE question_bank and start fresh (no backfill needed)

### Code State
**Completed:**
- `studybuddy/backend/db/sql/schema.sql` - Added subtopics table
- `studybuddy/backend/db/sql/migration_add_subtopics.sql` - Migration file
- `studybuddy/backend/db/repository.py` - Added subtopic methods to protocol
- `studybuddy/backend/db/postgres_repo.py` - Implemented subtopic methods
- `scripts/` - Multiple helper scripts for generation and seeding

**Not Yet Modified (Phase 2 work):**
- `studybuddy/backend/db/repository.py` - Need to add `subtopic` param to question methods
- `studybuddy/backend/db/postgres_repo.py` - Need subtopic filtering in list_questions/count_questions
- `studybuddy/backend/services/question_picker.py` - Need select_next_subtopic() function
- `studybuddy/backend/services/genai.py` - Need to add subtopic to GenerationContext
- `studybuddy/backend/routes/questions.py` - Need to handle subtopic selection
- `studybuddy/backend/models.py` - Need to update QuestionRequest/QuestionResponse

## Next Steps / Phase 2 🚀

### 2.0 Clear Question Bank
```sql
TRUNCATE TABLE question_bank CASCADE;
TRUNCATE TABLE attempts CASCADE;
TRUNCATE TABLE seen_questions CASCADE;
```

### 2.1 Add Subtopic Parameter to Repository Methods
- Update `list_questions()` signature to accept `subtopic` parameter
- Update `count_questions()` signature to accept `subtopic` parameter
- Implement subtopic filtering in queries

### 2.2 Create Subtopic Selection Logic
- Implement `select_next_subtopic()` function in `question_picker.py`
- **Only auto-select when user doesn't provide subtopic**
- Selection based on:
  1. Unseen question count (prioritize subtopics with more unseen)
  2. Sequence order (follow curriculum progression for ties)

### 2.3 Update Question Generation
- Add `subtopic` to `GenerationContext` dataclass
- Update `_build_prompt()` to include subtopic in OpenAI prompt
- Ensure generated questions include proper `sub_topic` value

### 2.4 Update Routes and API Models
- Update `QuestionRequest` to accept optional `subtopic`
- Update `QuestionResponse` to return `selected_subtopic`
- Modify `/fetch` endpoint to:
  - Use user-provided subtopic if given
  - Auto-select subtopic if not provided
  - Return which subtopic was used

### 2.5 Update Stock Management
- Check stock levels per-subtopic (not per-topic)
- Only generate when subtopic stock < MIN_STOCK_THRESHOLD

## Key Design Decisions 📝

1. **Static Subtopics**: Generated once via script, stored as seed data (not dynamic per user)
2. **Clean Slate**: TRUNCATE question_bank instead of backfilling (acceptable for dev)
3. **User Override**: Auto-selection only when user doesn't specify subtopic
4. **On-Demand Generation**: Questions generated with subtopic context as needed
5. **Per-Subtopic Inventory**: Stock management at subtopic level for better coverage

## Files Created This Session
- `/scripts/generate_subtopic_seeds.py`
- `/scripts/seed_subtopics.py`
- `/scripts/apply_subtopics_migration.py`
- `/scripts/run_generate_subtopics.sh`
- `/scripts/run_seed_subtopics.sh`
- `/scripts/run_migration.sh`
- `/studybuddy/backend/db/sql/seed_subtopics.json`
- `/studybuddy/backend/db/sql/migration_add_subtopics.sql`
- `/.claude.json` (project-specific config)
- `/CLAUDE_PLAN.md`
- `/CLAUDE_PLAN2.md`

## Files Modified This Session
- `studybuddy/backend/db/sql/schema.sql` - Added subtopics table + indexes
- `studybuddy/backend/db/repository.py` - Added subtopic methods to protocol
- `studybuddy/backend/db/postgres_repo.py` - Implemented subtopic repository methods
- `scripts/generate_subtopic_seeds.py` - User modified to add Eureka Math reference

## Important Notes
- MCP server `context7` added to `.claude.json` but not actively used
- OpenAI API key required and configured in `.env`
- Migration is idempotent (safe to run multiple times)
- Seed loading is idempotent (checks for existing records)
- All 130 OpenAI API calls completed successfully during generation

## Key Commands for Resumption
```bash
# Check subtopics in database
python3 -c "from studybuddy.backend.db.repository import build_repository; \
repo = build_repository(); \
print(f'Math: {repo.count_subtopics(subject=\"math\")}'); \
print(f'Reading: {repo.count_subtopics(subject=\"reading\")}')"

# View a few subtopics
python3 -c "from studybuddy.backend.db.repository import build_repository; \
repo = build_repository(); \
topics = repo.list_subtopics('math', 1, 'addition')[:3]; \
for t in topics: print(f'{t[\"subtopic\"]}: {t[\"description\"]}')"

# Start dev server
make dev

# Run Phase 2 when ready
# Follow CLAUDE_PLAN2.md for step-by-step implementation
```

## Estimated Remaining Time
- Phase 2 (Question Selection): ~2 days
- Phase 3 (Question Generation): ~1 day
- Phase 4 (Stock Management): ~1 day
- Testing & Polish: ~1 day

**Total remaining: ~5 days for complete subtopic system**
