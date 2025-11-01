# studybuddy Usage Guide

## Highlights
- **Modern React Frontend**: Full React 19 + TypeScript UI with authentication, child management, adaptive practice sessions, and real-time progress tracking.
- **Auth-backed parent portal**: Sign up or log in to receive bearer tokens securing child profiles, question delivery, and progress insights.
- **Child-centric quiz loops**: Parents create child records (grade + ZIP) and fetch unseen, grade-aware questions with no repeats after correct answers.
- **Adaptive difficulty**: Questions automatically adjust based on child's performance history (≥95% → hard, ≥80% → progressive, <80% → easy).
- **Progress analytics**: Every attempt logs correctness and streaks, enabling real-time accuracy and subject-level trends.
- **Subtopic system**: Intelligent subtopic selection with 1,275+ subtopics prioritizing unseen questions and sequence order.
- **Eureka Math integration**: Mathematics questions follow Eureka Math (EngageNY) curriculum; other subjects use Common Core.
- **Session tracking**: Automatic session management for practice insights (FEAT-101).
- **Adaptive + generative**: When the local bank runs low, a pacing-aware, OpenAI-backed generator (mockable for offline dev) tops it up automatically.
- **Seed data ready**: In-memory repository ships with curriculum-aligned standards and seed MCQs; swap `STUDYBUDDY_DATA_MODE` to `supabase` to exercise a hosted Postgres instance.
- **Deployable baseline**: Dockerfile and Render blueprint streamline promotion from local to hosted environments.

## Running Locally

### Backend Setup
1. **Set up environment**
   ```bash
   python3 -m venv testai-env
   source testai-env/bin/activate
   make install-dev
   cp .env.example .env
   # Configure environment variables:
   # - STUDYBUDDY_DATA_MODE=memory (or supabase for production)
   # - STUDYBUDDY_MOCK_AI=1 (to avoid real OpenAI calls locally)
   # - SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (if using supabase mode)
   # - OPENAI_API_KEY (for AI-generated questions)
   ```

2. **Run FastAPI backend**
   ```bash
   make dev
   ```
   The API listens on `http://localhost:8000`. Health check: `http://localhost:8000/healthz`

### Frontend Setup
1. **Navigate to React app directory**
   ```bash
   cd src/ui/web
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **For Development** - Run with hot-reload (requires backend running on port 8000):
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173` with API proxy to backend.

4. **For Production** - Build and serve through FastAPI:
   ```bash
   npm run build
   # The build outputs to dist/ which FastAPI serves automatically
   # Visit http://localhost:8000 to access the React app
   ```

### Running Tests
```bash
# Backend tests
make test

# Frontend type checking
cd src/ui/web && npm run typecheck

# Frontend linting
cd src/ui/web && npm run lint
```

## Using the React Frontend

The primary way to use studybuddy is through the React web interface:

1. **Access the app**: Open `http://localhost:8000` in your browser (production build) or `http://localhost:5173` (development mode)
2. **Sign up**: Create a parent account with email and password
3. **Add children**: Create child profiles with name and grade
4. **Start practicing**: Select a child, subject, and optionally a topic/subtopic to begin adaptive practice
5. **Track progress**: View real-time accuracy, streaks, and subject breakdowns in the Progress panel

## API Testing with `curl`

For API-level testing and automation, you can interact directly with the backend endpoints.

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

# Fetch questions with automatic subtopic selection
curl -s "$API/questions/fetch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","subject":"math","limit":5}'

# Or specify a topic for targeted practice
curl -s "$API/questions/fetch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","subject":"math","topic":"addition","limit":5}'

# Or specify both topic and subtopic for precise practice
curl -s "$API/questions/fetch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","subject":"math","topic":"addition","subtopic":"single-digit addition","limit":5}'
```
Pick the first question ID and correct answer for the next call.

### 4. Submit an attempt
```bash
QUESTION_ID="<question-id>"
ANSWER="<chosen-option>"
curl -s "$API/attempts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"child_id":"'"$CHILD_ID"'","question_id":"'"$QUESTION_ID"'","selected":"'"$ANSWER"'","time_spent_ms":2500}'
```
The `time_spent_ms` field tracks how long the child spent on the question (in milliseconds), enabling time-based analytics.

### 5. View child progress & standards
```bash
# View child's overall progress (accuracy, streak, subject breakdown)
curl -s "$API/progress/$CHILD_ID" -H "Authorization: Bearer $TOKEN"

# List available standards (Common Core + Eureka Math)
curl -s "$API/standards" -H "Authorization: Bearer $TOKEN"

# List available subtopics for a subject and grade
curl -s "$API/subtopics?subject=math&grade=3" -H "Authorization: Bearer $TOKEN"
```

### 6. (Optional) Pre-generate questions as an admin
```bash
# Generate questions for a specific topic
curl -s "$API/admin/generate" \
  -H "X-Admin-Token: change-me" \
  -H "Content-Type: application/json" \
  -d '{"subject":"math","topic":"fractions","grade":3,"count":5}'

# Generate questions for a specific subtopic
curl -s "$API/admin/generate" \
  -H "X-Admin-Token: change-me" \
  -H "Content-Type: application/json" \
  -d '{"subject":"math","topic":"fractions","subtopic":"comparing fractions","grade":3,"count":5}'
```
Populate `STUDYBUDDY_ADMIN_TOKEN` in `.env` to protect this endpoint.

**Note**: Math questions use **Eureka Math (EngageNY)** curriculum standards, while other subjects use Common Core.

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
# Core schema (parents, children, question_bank, attempts, standards, parent_tokens)
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/schema.sql

# Row-level security policies
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/policies.sql

# Subtopics table (1,275+ subtopics for K-12 math and reading)
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/migration_add_subtopics.sql

# Sessions table (for session tracking and insights - FEAT-101)
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/migration_add_sessions.sql
```

### 4. Seed reference data
```bash
# Seed Common Core and Eureka Math standards
psql "$SUPABASE_DB_URL" -f studybuddy/backend/db/sql/seed_standards.sql

# Seed 1,275+ subtopics using automation script
./scripts/run_seed_subtopics.sh

# Seed question bank
./scripts/run_update_seed_questions.sh
```

For production Supabase instances, use the environment variable approach:
```bash
# Set your Supabase connection details
export SUPABASE_DB_PASSWORD="your-password"

# Run migrations and seeds
PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h your-db-host.supabase.com -p 6543 \
  -U postgres.yourproject -d postgres -f studybuddy/backend/db/sql/schema.sql
```

### 5. Inspect data

For **local Supabase** (Docker):
```bash
psql "$SUPABASE_DB_URL" -c 'select id, email, created_at from parents limit 5;'
psql "$SUPABASE_DB_URL" -c 'select id, parent_id, name, grade from children limit 5;'
psql "$SUPABASE_DB_URL" -c 'select id, child_id, question_id, correct, created_at from attempts order by created_at desc limit 10;'
psql "$SUPABASE_DB_URL" -c 'select subject, grade, standard_ref from standards order by grade, subject limit 10;'
psql "$SUPABASE_DB_URL" -c 'select count(*) as total_subtopics, subject from subtopics group by subject;'
```
Supabase Studio UI: http://localhost:54323/project/default/editor

For **remote Supabase** (production):
```bash
# Set connection credentials
export SUPABASE_DB_PASSWORD="your-db-password"
DB_HOST="aws-1-us-west-1.pooler.supabase.com"
DB_USER="postgres.yourproject"

# Inspect tables
PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h $DB_HOST -p 6543 -U $DB_USER -d postgres \
  -c "SELECT count(*) as total_subtopics, subject FROM subtopics GROUP BY subject;"

PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h $DB_HOST -p 6543 -U $DB_USER -d postgres \
  -c "SELECT id, parent_id, name, grade FROM children LIMIT 5;"
```


### 6. Switch FastAPI to Supabase mode
Add to `.env` (or export) before launching the backend:
```bash
# Data persistence mode (memory for dev, supabase for production)
STUDYBUDDY_DATA_MODE=supabase

# Supabase connection
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI API for question generation
OPENAI_API_KEY=sk-...
STUDYBUDDY_MOCK_AI=0  # Set to 1 to use mock AI (no OpenAI calls)

# Admin token for /admin/generate endpoint
STUDYBUDDY_ADMIN_TOKEN=your-secret-token
```

**Key Points**:
- `parent_tokens` table backs bearer token lookups in Supabase mode
- The in-memory repository remains the default for rapid iteration
- Removing `STUDYBUDDY_MOCK_AI` (or setting to `0`) enables real OpenAI generation
- Math questions use **Eureka Math (EngageNY)** curriculum
- React frontend automatically adjusts difficulty based on child's performance
- Subtopic selection prioritizes unseen questions within sequence order

Use these instructions to validate both the REST API, React frontend, and the backing Postgres environment locally or in production.
