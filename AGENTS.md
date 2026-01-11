# Repository Guidelines

This guide helps contributors work efficiently in this codebase. Keep changes small, focused, and aligned with the structure and standards below.

## Project Structure & Module Organization
- Source code lives in `src/`:
  - Core logic: `src/core/`
  - UI components/views: `src/ui/`
  - External adapters/integrations: `src/services/`
- Tests mirror `src/` under `tests/` (e.g., `tests/core/quizEngine.spec.ts`).
- Reusable fixtures: `tests/fixtures/`. Static assets: `assets/`. Scripts: `scripts/`.
- Until app code lands, check `README.md` for flows, deps, and roadmap.

## Build, Test, and Development Commands
- `npm install` — install dependencies (rerun when lockfile changes).
- `npm run dev` — start local playground at `http://localhost:5173`.
- `npm run build` — produce a production bundle in `dist/`.
- `npm run lint` — run static checks; auto-fix with `npm run lint -- --fix`.
- `npm run test` — execute unit tests; add `-- --coverage` for a report.

## Coding Style & Naming Conventions
- Language: TypeScript with ES2020 modules, 2-space indentation.
- Naming: React components in PascalCase; helpers/hooks in camelCase; shared constants in SCREAMING_SNAKE_CASE.
- Keep modules narrowly scoped; export a single default or a minimal, intentional API.
- Run `npm run lint -- --fix` before opening PRs.

## Testing Guidelines
- Framework: Vitest for unit tests (Playwright E2E planned).
- File names: unit `*.spec.ts`; integration `*.test.ts`.
- Coverage target ≥80%: `npm run test -- --coverage`.
- Store sample data under `tests/fixtures/`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat: add adaptive scoring`), ≤72‑char subject.
- Pair code and relevant docs updates in the same commit when related.
- PRs must include: clear objective summary, linked issues, `npm run test` output, and screenshots for UI changes. Note configuration updates and any new dependencies. Wait for green CI and at least one maintainer review.

## Security & Configuration Tips
- Keep secrets in `.env.local` (git‑ignored). Update `.env.example` when inputs change.
- Sanitize datasets, verify third‑party licenses, and flag new dependencies during review.

