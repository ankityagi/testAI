# StudyBuddy — Upcoming Features

This document tracks near-term enhancements and how they fit the product. Each item includes a brief objective, core UX, data needs, and implementation notes so work can be split across frontend and backend.

## 1) Session Metrics & Insights ("Session Insights") [Tag: FEAT-101]
- Objective: Summarize progress at session end; highlight strengths/weaknesses; compare vs. historical; indicate trend (improving/flat/declining); include time-to-solve.
- UX:
  - Session summary card: accuracy, avg time/answer, streaks, question count.
  - Concept breakdown: per subtopic accuracy and time; badges for “mastered”/“needs practice”.
  - Trend chip: improving/flat/declining vs. last 7 days and lifetime.
- Data/Model:
  - Capture per-attempt `duration_ms`, `subtopic_id`, `difficulty_level`, `correct`.
  - Aggregates: per-session (in-memory + persisted), rolling 7/30-day, lifetime.
  - Trend logic: compare session accuracy/time vs. rolling baseline with small n safeguards.
- Implementation:
  - Backend: compute aggregates on write; expose `GET /sessions/{id}/summary` and `GET /progress/{child_id}?window=7d`.
  - Frontend: `SessionSummary` view; charts (sparklines for accuracy/time); export/share as image.

## 5) Parent Dashboard ("Parent View") [Tag: FEAT-102]
- Objective: A dedicated screen for guardians with granular metrics, trends, and guidance.
- UX:
  - Per-child overview: accuracy, time-on-task, recent streaks, subject/subtopic highlights.
  - Insights: areas to focus on, performance vs. grade level, interest hints (topics attempted most).
- Data/Model:
  - Aggregates by child → subject → subtopic; trend deltas (7/30-day), difficulty mix.
  - Benchmarks by grade for “at/above/below level” signals.
- Implementation:
  - Backend: extend progress endpoints to return parent-focused aggregates; optional grade benchmarks table.
  - Frontend: `/parents` route; cards + charts; drill-down to attempts.

## 2) Quiz Mode (Targeted Subtopics) ("Targeted Quiz") [Tag: FEAT-103]
- Objective: Create quizzes spanning one or more subtopics with a fixed count; render multiple questions per page with free-response fields.
- UX:
  - Quiz builder: choose subtopics, count, difficulty.
  - Play view: grid/list of N questions; inputs (numeric/text) instead of multiple choice; inline validation feedback.
  - Submit all → review screen with correct answers and explanations.
- Data/Model:
  - Quiz entity: id, child_id, subtopics[], count, difficulty, created_at, due_at (optional).
  - Question variant format supporting short-answer; tolerance rules for numeric.
- Implementation:
  - Backend: `POST /quizzes` (create), `GET /quizzes/{id}`, `POST /quizzes/{id}/submit` (batch attempts).
  - Frontend: routes `/quizzes/new`, `/quizzes/:id`, components for free-response inputs and batch submit.

## 3) Quiz Tournament (Friends) ("Tournament Mode") [Tag: FEAT-104]
- Objective: Compete on the same quiz; rank by accuracy first, then total time.
- UX:
  - Create/join tournament link; lobby shows participants and start time.
  - Live leaderboard during/after quiz; tie-breaker by total time.
- Data/Model:
  - Tournament: id, quiz_id, host_id, participants[], state, start_at.
  - Scores: per participant accuracy/time; optional anti-cheat flags.
- Implementation:
  - Backend: `POST /tournaments`, `POST /tournaments/{id}/join`, `GET /tournaments/{id}/leaderboard`.
  - Realtime: poll or lightweight websocket for live leaderboard (future).
  - Frontend: `/tournaments/:id` view with leaderboard and share link.

## 4) Share Quiz Snapshot ("Share Snapshot") [Tag: FEAT-105]
- Objective: Let users share a static snapshot of a quiz or session summary with friends.
- UX:
  - “Share” button on results pages; generate image (or PDF) preview.
  - Options: copy link, download image, share to socials (client-side share if supported).
- Implementation:
  - Frontend-only MVP: render summary card to canvas (html2canvas) and save/share.
  - Backend (optional): signed URL rendering for consistent branding and link longevity.

## 5) Allow user to see past questions 

## Cross-Cutting Notes
- Privacy: Avoid exposing PII in shared artifacts; use signed, expiring links.
- Performance: Precompute aggregates on write; paginate heavy lists; cache common summaries.
- Accessibility: Keyboard navigation, ARIA labels, color-contrast (WCAG AA) across new views.
- Telemetry: Track time-to-complete, error rates, share clicks; use to tune adaptive logic.
