# studybuddy Usage Guide

## Highlights
- **Auth-backed parent portal**: Sign up or log in to receive bearer tokens securing child profiles, question delivery, and progress insights.
- **Child-centric quiz loops**: Parents create child records (grade + ZIP) and fetch unseen, grade-aware math questions with no repeats after correct answers.
- **Progress analytics**: Every attempt logs correctness and streaks, enabling `/progress/{child_id}` to reveal accuracy and subject-level trends.
- **Adaptive + generative**: When the local bank runs low, a pacing-aware, OpenAI-backed generator (mockable for offline dev) tops it up automatically.
- **Seed data ready**: In-memory repository ships with Common Core-aligned standards and seed MCQs; swap `STUDYBUDDY_DATA_MODE` to `supabase` to exercise a hosted Postgres instance.
- **Deployable baseline**: Dockerfile and Render blueprint streamline promotion from local to hosted environments.

## Running Locally
1. **Set up environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   cp .env.example .env
   # leave STUDYBUDDY_MOCK_AI=1 to avoid real OpenAI calls locally
   ```
2. **Run FastAPI backend**
   ```bash
   make dev
   ```
   The API listens on `http://localhost:8000`; static placeholder UI lives under `http://localhost:8000/static/`.
3. **Execute tests** (optional)
   ```bash
   make test
   ```

## Quick Test with `curl`
Set a helper for the base URL:
```bash
API="http://localhost:8000"
```

### 1. Sign up a parent
```bash
curl -s "$API/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Secret123"}'
```
Capture the returned `access_token` for subsequent calls:
```bash
TOKEN=$(curl -s "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Secret123"}' | jq -r '.access_token')
```

### 2. Create a child profile
```bash
curl -s "$API/children" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex","grade":1,"zip":"10001"}'
```
Save the child ID (e.g., via `jq -r '.id'`).

### 3. Fetch questions
```bash
CHILD_ID="<child-id-from-create>"
curl -s "$API/questions/fetch" \Termin
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","subject":"math","limit":5}'
```
Pick the first question ID and correct answer for the next call.

### 4. Submit an attempt
```bash
QUESTION_ID="<question-id>"
ANSWER="<chosen-option>"
curl -s "$API/attempts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","question_id":"'"$QUESTION_ID"'","selected":"'"$ANSWER"'","time_spent_ms":1500}'
```

### 5. View child progress & standards
```bash
curl -s "$API/progress/$CHILD_ID" -H "Authorization: Bearer $TOKEN"

curl -s "$API/standards" -H "Authorization: Bearer $TOKEN"
```

### 6. (Optional) Pre-generate questions as an admin
```bash
curl -s "$API/admin/generate" \
  -H "X-Admin-Token: change-me" \
  -H "Content-Type: application/json" \
  -d '{"subject":"math","topic":"fractions","grade":3,"count":5}'
```
Populate `STUDYBUDDY_ADMIN_TOKEN` in `.env` to protect this endpoint.

## Supabase Postgres (local) Checklist
These commands assume a Supabase stack running locally (Docker or `supabase start`). Update credentials as needed.

### 1. Export connection info
```bash
export SUPABASE_DB_URL="postgres://postgres:postgres@localhost:54322/postgres"
```

### 2. Verify connectivity
```bash
psql "$SUPABASE_DB_URL" -c 'select now();'
```
If psql is unavailable, install via Homebrew (`brew install libpq`) and add it to your PATH.

### 3. Run schema migrations
```bash
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/schema.sql
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/policies.sql
```

### 4. Seed reference data
```bash
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/seed_standards.sql
```
JSON-based seeds can be inserted using 
```bash
psql "$SUPABASE_DB_URL" \
  -c "insert into question_bank (standard_ref, subject, grade, topic, sub_topic, difficulty, stem, options, correct_answer, rationale, source, hash)
      select standard_ref, subject, grade, topic, sub_topic, difficulty, stem, to_jsonb(options), correct_answer, rationale, source, hash
      from json_populate_recordset(null::record,
        $(cat studybuddy/backend/db/sql/seed_questions.json)
      );"
```
(or provide your own loader script).

### 5. Inspect data
```bash
psql "$SUPABASE_DB_URL" -c 'select id, email, created_at from parents limit 5;'
psql "$SUPABASE_DB_URL" -c 'select id, parent_id, name, grade from children limit 5;'
psql "$SUPABASE_DB_URL" -c 'select id, child_id, question_id, correct, created_at from attempts order by created_at desc limit 10;'
psql "$SUPABASE_DB_URL" -c 'select subject, grade, standard_ref from standards order by grade, subject limit 10;'
```
http://localhost:54323/project/default/editor


### 6. Switch FastAPI to Supabase mode
Add to `.env` (or export) before launching the backend:
```bash
STUDYBUDDY_DATA_MODE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DB_URL="postgres://..."  # optional for custom scripts
```
`parent_tokens` backs bearer token lookups in Supabase mode. The in-memory repository remains the default for rapid iteration; removing `STUDYBUDDY_MOCK_AI` (or setting it to `0`) switches to real OpenAI generation when credentials are present.

Use these instructions to validate both the REST API and the backing Postgres environment locally.
