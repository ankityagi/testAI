# Repository Guidelines

## Project Structure & Module Organization
testAI currently hosts planning docs only (`README.md`, `LICENSE`). As features land, create a `src/` folder for application code; keep domain logic in `src/core/`, interface components in `src/ui/`, and service integrations under `src/services/`. Mirror runtime modules inside `tests/` using matching paths, e.g. `tests/core/quizEngine.spec.ts`. Place static assets (sample question banks, illustrations) inside `assets/`, and shareable scripts under `scripts/`.

## Build, Test, and Development Commands
The project targets a Node/TypeScript toolchain. Ensure the following npm scripts exist and stay green:
- `npm install` installs workspace dependencies.
- `npm run dev` launches the local playground (Vite or Next.js) at `http://localhost:5173`.
- `npm run build` compiles a production bundle to `dist/`.
- `npm run lint` runs ESLint with the repository config.
- `npm run test` executes the automated suite.
Document any additional commands you introduce inside `README.md` and reference them in PRs.

## Coding Style & Naming Conventions
Use TypeScript, ES2020 modules, and 2-space indentation. Prefer descriptive PascalCase for React components, camelCase for variables/functions, and SCREAMING_SNAKE_CASE for constants. Run Prettier (`npm run lint -- --fix`) before opening PRs. Keep modules cohesive: export a single default or a focused set of named exports.

## Testing Guidelines
Rely on Vitest for unit tests and Playwright for end-to-end checks. Name unit test files `*.spec.ts` and integration tests `*.test.ts`. Target 80% line coverage minimum; add coverage reports with `npm run test -- --coverage`. When adding new quiz flows, include fixtures under `tests/fixtures/` to model grade-level standards.

## Commit & Pull Request Guidelines
Follow Conventional Commits (e.g., `feat: add adaptive scoring`) with <=72 character subjects and optional bodies. Group related changes per commit and update docs alongside code. Pull requests must include: objective summary, testing evidence (`npm run test` output), screenshots for UI changes, and linked issue numbers. Request review from at least one maintainer and wait for CI success before merging.

## Security & Configuration Tips
Store secrets (API keys, dataset URLs) in `.env.local`; never commit them. Provide `.env.example` updates when configuration changes. Sanitize sample datasets before uploading and confirm new third-party dependencies have permissive licenses.
