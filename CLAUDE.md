# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
python3 -m venv testai-env
source testai-env/bin/activate
make install-dev
```

### Running the Application

**Backend:**
```bash
make dev                # Start FastAPI server with autoreload on port 8000
```

**Frontend:**
```bash
cd src/ui/web
npm install             # First time only
npm run dev             # Development server on port 5173 with hot-reload
npm run build           # Production build to dist/ (served by FastAPI)
```

**Production Mode:**
After running `npm run build`, access the React app at `http://localhost:8000` (served by FastAPI).

### Testing and Code Quality

**Backend:**
```bash
make test              # Run pytest tests
make lint              # Compile check with compileall
make format            # Format code with ruff
```

**Frontend:**
```bash
cd src/ui/web
npm run typecheck      # TypeScript type checking
npm run lint           # ESLint checking
npm run format:check   # Check code formatting
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database
- `OPENAI_API_KEY` for AI-generated questions
- `STUDYBUDDY_DATA_MODE=memory` for local dev, `supabase` for production
- `STUDYBUDDY_MOCK_AI=1` for offline AI generation testing

## Architecture Overview

### Project Structure

**Backend:**
- **studybuddy/backend/**: FastAPI application with modular route organization
- **studybuddy/backend/app.py**: Main FastAPI entrypoint with router registration and React integration
- **studybuddy/backend/models.py**: Pydantic schemas for all request/response bodies
- **studybuddy/backend/routes/**: Individual route modules (auth, children, questions, etc.)
- **studybuddy/backend/services/**: Business logic (question_picker, genai, hashing, validators)
- **studybuddy/backend/db/**: Database clients (postgres_repo) and SQL schema/seeds
- **studybuddy/tests/**: Test structure mirrors backend organization

**Frontend:**
- **src/ui/web/**: React 19 + TypeScript frontend application
- **src/ui/web/src/components/**: Reusable UI components (Button, Card, Input, etc.)
- **src/ui/web/src/components/panels/**: Feature panels (ChildrenPanel, PracticePanel, ProgressPanel)
- **src/ui/web/src/contexts/**: React contexts for state management (AuthContext, ChildrenContext, PracticeContext)
- **src/ui/web/src/pages/**: Page components (Auth, Dashboard)
- **src/ui/web/src/services/**: API client services with axios interceptors
- **src/ui/web/dist/**: Production build (automatically served by FastAPI at root `/`)

**Scripts:**
- **scripts/**: Database migration and seeding scripts for subtopics and questions

### Key Components

**Authentication Flow**: Service-managed tokens via `/auth/signup` and `/auth/login` with bearer token validation for protected routes.

**Data Modes**: Supports both in-memory (development) and Supabase (production) data persistence through configurable repository pattern.

**Question Generation**: Hybrid system using seeded questions with fallback to OpenAI generation when inventory is low. Includes deduplication via hashing and adaptive difficulty. Math questions use Eureka Math (EngageNY) standards, other subjects use Common Core.

**Child Management**: Grade-aware profiles that drive question selection and standards alignment (Eureka Math for mathematics, Common Core for other subjects).

**Adaptive Difficulty**: Baseline implementation in `question_picker.py` adjusts difficulty based on performance history (≥95% → hard, ≥80% → progressive, <80% → easy). Advanced features planned in CLAUDE_PLAN4.

**Subtopic System**: Intelligent subtopic selection prioritizes topics with more unseen questions, maintaining sequence order for structured learning progression.

### Development Patterns

**Backend:**
- All route modules follow consistent FastAPI router pattern
- Pydantic models provide request/response validation with custom validators
- Database operations abstracted through repository pattern for mode switching
- Environment-based configuration for external services (Supabase, OpenAI)
- Comprehensive logging with `[PICKER]`, `[ADAPTIVE]`, `[FETCH_BATCH]` prefixes for debugging

**Frontend:**
- React Context API for global state management (Auth, Children, Practice)
- Functional setState updates to avoid stale closure issues
- Custom event system for cross-component communication (e.g., `answer-submitted` event)
- Axios interceptors for automatic token injection and trailing slash handling
- TypeScript strict mode with comprehensive type definitions
- Component-level state with useState/useEffect hooks
- Inline styles with theme constants for consistent design

### Phase-Based Development
The codebase follows a 4-phase development plan (see PLAN_FILE.md):
- Phase 1: Developer foundations and scaffolding ✅
- Phase 2: Core authentication and quiz flows ✅
- Phase 3: AI generation and adaptive delivery ✅
- **React Frontend (CLAUDE_PLAN3)**: Full UI implementation ✅
- Phase 4: Advanced adaptive features (CLAUDE_PLAN4) 🚧

### API Structure
Core endpoints include `/children` (CRUD), `/questions/fetch` (adaptive delivery), `/attempts` (logging), `/progress/{child_id}` (analytics), and `/admin/generate` (batch creation).

### React Integration
- FastAPI serves React production build from `src/ui/web/dist/` at root path `/`
- API routes take precedence over catch-all React route
- Development: React dev server on port 5173 with proxy to FastAPI on port 8000
- Production: Single-server deployment with React and API on port 8000

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- Use claude_changelog file to document all changes added to the code
- along with each PR update the README file, and USAGE_FILE
- Always use gh cli when working with github and make sure to track all new files
- always update checkpoint file, and readme  when making PR
- when working on a checklist remember to update the list when any item is complete
- when working on a checklist remember to update the list when any item is complete