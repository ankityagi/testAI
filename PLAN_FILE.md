# Phased Execution Plan for studybuddy

## Phase 1 — Foundations & Developer Experience
- Establish repo scaffold matching provided layout (FastAPI backend, static frontend bundle, infrastructure files).
- Configure environment handling: `.env.example`, Supabase keys, OpenAI API key placeholders, Render deployment variables.
- Define database schema & migrations: translate `schema.sql`, create seed data stubs, set up Supabase RLS policies and local dev strategy.
- Implement FastAPI app shell (`app.py`, router registration, dependency wiring) and static file serving.
- Stub frontend pages with basic HTML/CSS/JS skeletons and shared API client; set up build tooling (Vite or simple bundler) for local iteration.
- Add project automation: `Makefile`/npm scripts (format, lint, test), pre-commit hooks, Dockerfile baseline, Render blueprint.
- Success criteria: developers can run backend locally, hit `/healthz`, serve placeholder frontend, run lint/test stubs.

## Phase 2 — Core Product Flows
- Authentication: integrate Supabase Auth client/server helpers (`deps.py`), session validation middleware, login/signup flows in frontend.
- Parent & child management: implement `/children` CRUD, Pydantic models, DB repositories, responsive UI for managing profiles.
- Standards catalog: ingest `seed_standards.sql/json`, expose `/standards`, display browse/filter UI to help parents align topics.
- Question delivery: build `/questions/fetch` pipeline pulling unseen seeded questions, enforcing validators and hashing for dedupe.
- Attempt logging: implement `/attempts` endpoint, persist correctness/time, update frontend quiz flow with immediate feedback.
- Progress tracking: deliver `/progress/{child_id}` aggregation and visualize streaks/accuracy on goodbye page.
- Success criteria: parent can log in, create child, launch quiz session with seeded questions, track progress end-to-end without AI generation.

## Phase 3 — Intelligent Question Generation & Adaptation
- Pacing engine: implement `pacing.py` to map grade + month (from ZIP-based school calendar heuristics) to recommended topics.
- OpenAI integration: build `genai.py` prompt templates, error handling, response validation (`validators.py`), hashing/dedupe pipeline.
- Adaptive difficulty: enhance `question_picker.py` to consider prior attempts, correctness streak, and difficulty tiers when selecting/generating questions.
- Background generation: create task runner (FastAPI background tasks or simple job queue) for `/admin/generate` and on-demand top-ups when stock < threshold.
- Guarantee uniqueness: persist `seen_questions`, enforce logic to skip repeats after correct answers, gracefully recycle missed items for remediation.
- Frontend updates: expose topic overrides, loading states for generated questions, and progressive difficulty indicators.
- Success criteria: system can dynamically create validated MCQs per child/topic, scale difficulty, and avoid repeats, with robust fallback to seeded bank.

## Phase 4 — Polish, Analytics, and Deployment Readiness
- Analytics & visualization: enrich goodbye page with charts (e.g., Chart.js) showing accuracy by standard/topic, highlight strengths/gaps.
- Admin & support tooling: secure `/admin/generate`, add audit logging, basic admin dashboard for question inventory and pacing presets.
- Quality gates: write comprehensive unit/contract tests (backend services, validators, routers) and Playwright smoke tests for critical flows; set up CI.
- Performance & security hardening: enable Supabase RLS policies, audit API error handling, add rate limiting/caching where sensible, sanitize AI outputs.
- Deployment: finalize Dockerfile, Render `render.yaml`, document deployment steps and monitoring/alerts; provide seed scripts for Supabase.
- Documentation: expand README with setup, dev workflows, troubleshooting, architecture diagrams, and future roadmap.
- Success criteria: production-sane POC ready for Render deployment, with monitoring, tests, and docs supporting ongoing iteration.

## Phase 5 — Future Enhancements (Post-POC Considerations)
- Personalized learning paths using mastery models and spaced repetition scheduling.
- Gamification layers (badges, avatar customization, parent dashboards for multiple children).
- Expanded subject coverage (science/social studies), multimodal content (audio, images), accessibility improvements.
- Integration with school calendars/APIs for real-time pacing updates and teacher collaboration features.
- Data export/compliance tooling (FERPA/GDPR), parental controls, and consent management workflows.
