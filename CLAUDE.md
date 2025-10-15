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
```bash
make dev                # Start FastAPI server with autoreload on port 8000
```

### Testing and Code Quality
```bash
make test              # Run pytest tests
make lint              # Compile check with compileall
make format            # Format code with ruff
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database
- `OPENAI_API_KEY` for AI-generated questions
- `STUDYBUDDY_DATA_MODE=memory` for local dev, `supabase` for production
- `STUDYBUDDY_MOCK_AI=1` for offline AI generation testing

## Architecture Overview

### Project Structure
- **studybuddy/backend/**: FastAPI application with modular route organization
- **studybuddy/backend/app.py**: Main FastAPI entrypoint with router registration
- **studybuddy/backend/models.py**: Pydantic schemas for all request/response bodies
- **studybuddy/backend/routes/**: Individual route modules (auth, children, questions, etc.)
- **studybuddy/backend/services/**: Business logic (hashing, validators)
- **studybuddy/backend/db/**: Database clients and SQL schema/seeds
- **studybuddy/tests/**: Test structure mirrors backend organization

### Key Components

**Authentication Flow**: Service-managed tokens via `/auth/signup` and `/auth/login` with bearer token validation for protected routes.

**Data Modes**: Supports both in-memory (development) and Supabase (production) data persistence through configurable repository pattern.

**Question Generation**: Hybrid system using seeded questions with fallback to OpenAI generation when inventory is low. Includes deduplication via hashing and adaptive difficulty.

**Child Management**: Grade-aware profiles that drive question selection and Common Core standards alignment.

### Development Patterns
- All route modules follow consistent FastAPI router pattern
- Pydantic models provide request/response validation with custom validators
- Database operations abstracted through repository pattern for mode switching
- Environment-based configuration for external services (Supabase, OpenAI)

### Phase-Based Development
The codebase follows a 4-phase development plan (see PLAN_FILE.md):
- Phase 1: Developer foundations and scaffolding ✅
- Phase 2: Core authentication and quiz flows ✅
- Phase 3: AI generation and adaptive delivery ✅
- Phase 4: Polish, testing, and deployment readiness

### API Structure
Core endpoints include `/children` (CRUD), `/questions/fetch` (adaptive delivery), `/attempts` (logging), `/progress/{child_id}` (analytics), and `/admin/generate` (batch creation).

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- Use claude_changelog file to document all changes added to the code
- along with each PR update the README file, and USAGE_FILE
- Always use gh cli when working with github and make sure to track all new files
