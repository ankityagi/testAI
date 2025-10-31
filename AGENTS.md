# Repository Guidelines

## Project Structure & Module Organization
- Keep production code in `src/`:
  - Core logic: `src/core/`
  - UI components/views: `src/ui/`
  - External adapters/integrations: `src/services/`
- Mirror structure in `tests/` (e.g., `tests/core/quizEngine.spec.ts`).
- Reusable fixtures: `tests/fixtures/`. Static assets: `assets/`. Scripts: `scripts/`.
- Until application code lands, consult `README.md` for flows, deps, and roadmap.
- Avoid new top‑level folders; extend existing layout.

## Build, Test, and Development Commands
- `npm install` — install deps (run when lockfile changes).
- `npm run dev` — start local playground at http://localhost:5173.
- `npm run build` — create production bundle in `dist/`.
- `npm run lint` — static checks; use `npm run lint -- --fix` to auto-format.
- `npm run test` — run unit tests; add `-- --coverage` for report.

## Coding Style & Naming Conventions
- Language: TypeScript, ES2020 modules, 2-space indentation.
- Naming: PascalCase for React components, camelCase for helpers/hooks, SCREAMING_SNAKE_CASE for shared constants.
- Keep modules narrowly scoped; export a single default or a small, intentional set of utilities.
- Run `npm run lint -- --fix` before opening PRs.

## Testing Guidelines
- Unit tests: Vitest. E2E (future): Playwright.
- File names: unit `*.spec.ts`; integration `*.test.ts`.
- Target ≥80% coverage: `npm run test -- --coverage`.
- Store sample data under `tests/fixtures/`.

## Commit & Pull Request Guidelines
- Conventional Commits (e.g., `feat: add adaptive scoring`), ≤72-char subject.
- Pair code and documentation changes in the same commit when related.
- PRs require:
  - Objective summary and linked issues.
  - `npm run test` output and screenshots (UI changes).
  - Note configuration updates and any new dependencies.
  - Wait for green CI and at least one maintainer review.

## Security & Configuration Tips
- Keep secrets in `.env.local` (git-ignored). Update `.env.example` when inputs change.
- Sanitize datasets, check third-party licenses, and flag new dependencies during review.
