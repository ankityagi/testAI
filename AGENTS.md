# Repository Guidelines

## Project Structure & Module Organization
Until application code lands, rely on `README.md` for current flows, dependencies, and roadmap. When shipping features, keep all code in `src/`: core logic in `src/core/`, UI in `src/ui/`, and external adapters in `src/services/`. Mirror that layout in `tests/` (for example, `tests/core/quizEngine.spec.ts`). Reusable fixtures belong in `tests/fixtures/`, static assets in `assets/`, and operational scripts in `scripts/`. Resist new top-level folders so future agents can locate work quickly.

## Build, Test, and Development Commands
Run `npm install` whenever the lockfile changes. Use `npm run dev` to serve the playground at http://localhost:5173 and verify interactive flows. Production bundles come from `npm run build`, which emits to `dist/`. Guard quality with `npm run lint`; append `-- --fix` for safe auto-formatting. Execute `npm run test` for regression coverage and add `-- --coverage` before requesting review. Document any extra Makefile or npm scripts in `README.md`.

## Coding Style & Naming Conventions
Author production code in TypeScript with ES2020 modules and 2-space indentation. Prefer PascalCase for React components, camelCase for helpers and hooks, and SCREAMING_SNAKE_CASE for shared constants. Keep modules narrowly scoped and export either a single default or a small, intentional set of named utilities. Always finish a branch with `npm run lint -- --fix` to avoid review churn.

## Testing Guidelines
Vitest covers unit suites; Playwright handles end-to-end scenarios once UI scaffolding arrives. Name unit specs `*.spec.ts` and integration suites `*.test.ts`. Store grade-level fixtures under `tests/fixtures/` and expand them as requirements grow. Target 80% coverage using `npm run test -- --coverage`, then highlight any intentional gaps in your PR notes.

## Commit & Pull Request Guidelines
Follow Conventional Commits (e.g., `feat: add adaptive scoring`) with ≤72-character subjects. Pair code and documentation changes in the same commit. Pull requests should state the objective, include `npm run test` output, attach UI screenshots when applicable, link related issues, and note configuration updates. Request at least one maintainer review and wait for green CI before merging.

## Security & Configuration Tips
Store secrets in `.env.local` and keep them out of git. Update `.env.example` whenever configuration inputs change so the next agent can bootstrap quickly. Sanitize datasets, check third-party licenses, and flag any new dependencies during review.
