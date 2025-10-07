# studybuddy

FastAPI + Supabase proof-of-concept that helps parents guide children through Common Core-aligned practice quizzes.

## Status
Phase 3 is complete: adaptive question delivery, OpenAI-powered (or mock) generation, pacing presets, and Supabase-ready data access build on the Phase 2 flows.

## Project Layout
```
studybuddy/
  backend/
    app.py
    deps.py
    models.py
    routes/
    services/
    db/
      supabase_client.py
      sql/
  tests/
Dockerfile
Makefile
render.yaml
requirements.txt
requirements-dev.txt
```

## Getting Started
1. Create a virtualenv and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
2. Configure environment variables:
   ```bash
   cp .env.example .env
   # fill in Supabase + OpenAI credentials (leave STUDYBUDDY_MOCK_AI=1 for offline generation)
   ```
3. Run the backend locally:
   ```bash
   make dev
   ```
   Visit `http://localhost:8000/static/` to view the placeholder UI. Health check is under `http://localhost:8000/healthz`.

4. (Optional) Run the automated tests:
   ```bash
   make test
   ```

### Authentication
- `POST /auth/signup` – create a parent account (in-memory for now) and receive a bearer token.
- `POST /auth/login` – authenticate an existing parent. Tokens must be supplied via `Authorization: Bearer <token>` for the protected routes listed below.

### Child & Quiz Workflow
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

## Next Steps
- Phase 2 will add Supabase authentication, child management flows, standards catalog, and initial quiz loop using seeded questions.
- See `PLAN_FILE.md` for the full phased roadmap.
