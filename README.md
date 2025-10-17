# studybuddy

FastAPI + React + Supabase proof-of-concept that helps parents guide children through Common Core-aligned practice quizzes.

## Status
**Phase 3 Complete**: Adaptive question delivery, OpenAI-powered (or mock) generation, pacing presets, and Supabase-ready data access.

**React Frontend**: Full React 19 + TypeScript frontend with authentication, child management, adaptive practice sessions, and real-time progress tracking.

## Project Layout
```
studybuddy/
  backend/
    app.py              # FastAPI app with React integration
    deps.py
    models.py
    routes/             # API endpoints
    services/           # Business logic
    db/
      supabase_client.py
      postgres_repo.py  # Database operations
      sql/              # Schema, migrations, seeds
  tests/
src/
  ui/
    web/                # React frontend
      src/
        components/     # UI components and panels
        contexts/       # React contexts (Auth, Children, Practice)
        pages/          # Auth and Dashboard pages
        services/       # API client services
      dist/             # Production build (served by FastAPI)
scripts/                # Database migration and seeding scripts
Dockerfile
Makefile
render.yaml
requirements.txt
requirements-dev.txt
```

## Getting Started

### Backend Setup
1. Create a virtualenv and install dependencies:
   ```bash
   python3 -m venv testai-env
   source testai-env/bin/activate
   pip install -r requirements-dev.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Fill in Supabase + OpenAI credentials
   # Set STUDYBUDDY_DATA_MODE=supabase for production
   # Set STUDYBUDDY_MOCK_AI=1 for offline AI generation testing
   ```

3. Run the backend:
   ```bash
   make dev
   ```
   Backend runs on `http://localhost:8000`. Health check: `http://localhost:8000/healthz`

### Frontend Setup
1. Navigate to the React app directory:
   ```bash
   cd src/ui/web
   ```

2. Install Node.js dependencies:
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

## Features

### React Frontend
- **Authentication**: Sign up and login with secure token-based authentication
- **Child Management**: Add, edit, and delete child profiles with grade tracking
- **Adaptive Practice Sessions**:
  - Select subject, topic, and subtopic for targeted practice
  - Dynamic difficulty adjustment based on performance history
  - Real-time question delivery with immediate feedback
  - Visual feedback with color-coded answer buttons
- **Progress Tracking**:
  - Overall accuracy and current streak display
  - Subject-level breakdown with visual progress bars
  - Real-time updates after each question
- **Modern UI**: Clean, accessible design with smooth animations and responsive layout

### API Endpoints

#### Authentication
- `POST /auth/signup` – create a parent account and receive a bearer token
- `POST /auth/login` – authenticate an existing parent. Tokens must be supplied via `Authorization: Bearer <token>` for protected routes

#### Child & Quiz Workflow
- `GET /children` / `POST /children` – manage child profiles.
- `POST /questions/fetch` – fetch unseen, grade-aware multiple choice questions. Falls back to OpenAI generation (or deterministic mock) when inventory is low, and queues background top ups.
- `POST /attempts` – log attempts, persist correctness, and prevent repeats on correct answers.
- `GET /progress/{child_id}` – pull streak/accuracy aggregates with a subject breakdown.
- `GET /standards` – reference Common Core-aligned standards backing the quiz content.
- `POST /admin/generate` – (protected by `X-Admin-Token`) pre-generate question batches for a subject/topic.

### Supabase Mode
- Set `STUDYBUDDY_DATA_MODE=supabase` and provide `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` to switch repositories.
- Apply `studybuddy/backend/db/sql/schema.sql` and `policies.sql` to your Supabase Postgres, then seed with `seed_standards.sql` and `seed_questions.json` helpers.
- Tokens remain service-managed via `parent_tokens` table for this phase; Supabase Auth integration can slot in without changing the HTTP contract.

## Tooling
- `make install` / `make install-dev` – bootstrap runtime or dev dependencies.
- `make dev` – run FastAPI with autoreload.
- `make lint` – bytecode compilation sanity check (placeholder until Phase 4).
- `make test` – run backend unit tests (Vitest/Playwright arrive in later phases).

## Technical Stack
- **Backend**: FastAPI, Python 3.11+, Pydantic v2
- **Frontend**: React 19, TypeScript, Vite
- **Database**: PostgreSQL via Supabase
- **AI**: OpenAI GPT-4 for question generation (with mock mode for testing)
- **Deployment**: Render.com ready (see `render.yaml`)

## Architecture Highlights
- **Adaptive Difficulty**: Questions automatically adjust based on child's performance history, streaks, and session accuracy
- **Smart Question Selection**: Prioritizes unseen questions, tracks per-child history, maintains question inventory with background generation
- **Subtopic System**: Intelligent subtopic selection based on unseen question availability and sequence order
- **Real-time Updates**: React contexts with event-driven architecture for instant UI updates
- **Type Safety**: End-to-end type safety with Pydantic models and TypeScript interfaces

## Development Roadmap
- ✅ **Phase 1**: Developer foundations and scaffolding
- ✅ **Phase 2**: Core authentication and quiz flows
- ✅ **Phase 3**: AI generation and adaptive delivery
- ✅ **React Frontend**: Full UI implementation with adaptive practice
- 🚧 **Phase 4**: Advanced adaptive features (see `CLAUDE_PLAN4`)
  - Session-based adjustments
  - Mastery detection
  - Recovery mechanisms
  - Enhanced telemetry

See `CLAUDE_PLAN3` and `CLAUDE_PLAN4` for detailed implementation plans.
