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
make test                                          # Run all pytest tests
pytest studybuddy/tests/backend/test_health.py    # Run specific test file
pytest studybuddy/tests/backend/test_health.py::test_healthz  # Run single test
make lint                                          # Compile check with compileall
make format                                        # Format code with ruff
```

**Frontend:**
```bash
cd src/ui/web
npm run typecheck      # TypeScript type checking
npm run lint           # ESLint checking
npm run format         # Format code with Prettier
npm run format:check   # Check code formatting
```

**Note:** Backend tests require dependencies to be installed (`make install-dev`). Some tests may fail if OpenAI or other external services are not configured.

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database
- `OPENAI_API_KEY` for AI-generated questions
- `STUDYBUDDY_DATA_MODE=memory` for local dev, `supabase` for production
- `STUDYBUDDY_MOCK_AI=1` for offline AI generation testing

### Database Operations

**Migration Scripts** (for Supabase mode):
```bash
./scripts/run_migration.sh                 # Apply subtopics migration
./scripts/run_quiz_migration.sh            # Apply quiz sessions migration
./scripts/run_sessions_migration.sh        # Apply practice sessions migration
./scripts/run_normalize_migration.sh       # Apply case normalization migration
```

**Seeding Scripts:**
```bash
./scripts/run_seed_subtopics.sh           # Seed 1,275+ subtopics
./scripts/run_seed_sample_questions.sh    # Seed sample questions
python scripts/check_question_inventory.py # Check question counts by subject/topic
python scripts/reset_question_bank.py     # Reset question bank (dev only)
```

## Architecture Overview

### Important Documentation Files
- **PLAN_FILE.md**: Original 4-phase development plan
- **CLAUDE_PLAN3**: React frontend implementation plan (complete)
- **CLAUDE_PLAN4**: Advanced adaptive features plan (in progress)
- **CLAUDE_PLAN_QUIZ**: Quiz mode implementation plan (60% complete)
- **CLAUDE_CHECKPOINT.md**: Development progress checkpoints
- **USAGE_FILE.md**: Comprehensive usage guide for end users
- **README.md**: Project overview and setup instructions

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

**Session Tracking (FEAT-101)**: Automatic practice session management tracks start/end times, questions answered, and performance metrics for analytics and insights.

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
- Vite path aliases configured in `vite.config.ts`:
  - `@/` → `src/`
  - `@/components` → `src/components/`
  - `@/pages` → `src/pages/`
  - `@/services` → `src/services/`
  - `@/core` → `../../core/`

### Phase-Based Development
The codebase follows a 4-phase development plan (see PLAN_FILE.md):
- Phase 1: Developer foundations and scaffolding ✅
- Phase 2: Core authentication and quiz flows ✅
- Phase 3: AI generation and adaptive delivery ✅
- **React Frontend (CLAUDE_PLAN3)**: Full UI implementation ✅
- Phase 4: Advanced adaptive features (CLAUDE_PLAN4) 🚧
- **Quiz Mode (CLAUDE_PLAN_QUIZ)**: Timed, classroom-style quiz mode - 60% complete (83/139 items)
  - Phase 1 (Backend): 73% complete - models, routes, services implemented
  - Phase 2 (Frontend): 100% complete - quiz UI and flows
  - Phase 3 (Behavior & Style): 100% complete - timer, grading, results
  - Phase 4 (Testing): 20% complete - in progress
  - Phase 5-6 (Docs & Rollout): Not started

### API Structure
Core endpoints include:
- `/auth/*`: Sign up, login, token management
- `/children`: CRUD operations for child profiles
- `/questions/fetch`: Adaptive question delivery with difficulty adjustment
- `/attempts`: Log question attempts and track correctness
- `/progress/{child_id}`: Analytics with streak/accuracy aggregates
- `/sessions/*`: Practice session tracking (FEAT-101)
- `/quiz/*`: Quiz session management, start, submit, results (CLAUDE_PLAN_QUIZ)
- `/standards`: Common Core and Eureka Math standards reference
- `/admin/generate`: Pre-generate question batches (admin only)

### React Integration
- FastAPI serves React production build from `src/ui/web/dist/` at root path `/`
- API routes take precedence over catch-all React route
- Development: React dev server on port 5173 with proxy to FastAPI on port 8000
- Production: Single-server deployment with React and API on port 8000

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests (see Testing and Code Quality section), not the whole test suite, for performance
- Along with each PR update the README.md and USAGE_FILE.md
- Always use gh cli when working with GitHub and make sure to track all new files
- Always update CLAUDE_CHECKPOINT.md and README.md when making PR
- When working on a checklist remember to update the list when any item is complete
- Remember to update the checklist when working from a plan document (CLAUDE_PLAN_QUIZ, CLAUDE_PLAN4, etc.)


## Visual Development & Testing

### Design System

The project follows S-Tier SaaS design standards inspired by Stripe, Airbnb, and Linear. All UI development must adhere to:

- **Design Principles**: `/context/design-principles.md` - Comprehensive checklist for world-class UI
- **Component Library**: Custom React components with inline styles and theme constants

### Quick Visual Check

**IMMEDIATELY after implementing any front-end change:**

1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages` ⚠️

This verification ensures changes meet design standards and user requirements.

### Comprehensive Design Review

For significant UI changes or before merging PRs, use the design review agent:

```bash
# Option 1: Use the slash command
/design-review

# Option 2: Invoke the agent directly
@agent-design-review
```

The design review agent will:

- Test all interactive states and user flows
- Verify responsiveness (desktop/tablet/mobile)
- Check accessibility (WCAG 2.1 AA compliance)
- Validate visual polish and consistency
- Test edge cases and error states
- Provide categorized feedback (Blockers/High/Medium/Nitpicks)

### Playwright MCP Integration

#### Essential Commands for UI Testing

```javascript
// Navigation & Screenshots
mcp__playwright__browser_navigate(url); // Navigate to page
mcp__playwright__browser_take_screenshot(); // Capture visual evidence
mcp__playwright__browser_resize(
  width,
  height
); // Test responsiveness

// Interaction Testing
mcp__playwright__browser_click(element); // Test clicks
mcp__playwright__browser_type(
  element,
  text
); // Test input
mcp__playwright__browser_hover(element); // Test hover states

// Validation
mcp__playwright__browser_console_messages(); // Check for errors
mcp__playwright__browser_snapshot(); // Accessibility check
mcp__playwright__browser_wait_for(
  text / element
); // Ensure loading
```

### Design Compliance Checklist

When implementing UI features, verify:

- [ ] **Visual Hierarchy**: Clear focus flow, appropriate spacing
- [ ] **Consistency**: Uses design tokens, follows patterns
- [ ] **Responsiveness**: Works on mobile (375px), tablet (768px), desktop (1440px)
- [ ] **Accessibility**: Keyboard navigable, proper contrast, semantic HTML
- [ ] **Performance**: Fast load times, smooth animations (150-300ms)
- [ ] **Error Handling**: Clear error states, helpful messages
- [ ] **Polish**: Micro-interactions, loading states, empty states

## When to Use Automated Visual Testing

### Use Quick Visual Check for:

- Every front-end change, no matter how small
- After implementing new components or features
- When modifying existing UI elements
- After fixing visual bugs
- Before committing UI changes

### Use Comprehensive Design Review for:

- Major feature implementations
- Before creating pull requests with UI changes
- When refactoring component architecture
- After significant design system updates
- When accessibility compliance is critical

### Skip Visual Testing for:

- Backend-only changes (API, database)
- Configuration file updates
- Documentation changes
- Test file modifications
- Non-visual utility functions


## Additional Context

- Design review agent configuration: `/.claude/agents/design-review-agent.md`
- Design principles checklist: `/context/design-principles.md`
- Custom slash commands available in `/.claude/commands/`:
  - `/design-review`: Conduct comprehensive design review of UI changes
  - `/ui-design-variations`: Generate premium UI design variations
  - `/test-react-component`: Test React component with Playwright
- Custom agents available in `/.claude/agents/`:
  - `design-review-agent.md`: Automated design and accessibility review
  - `premium-ui-designer.md`: Premium UI design and enhancement
