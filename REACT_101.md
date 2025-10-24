# React 101: Build a Web UI Against This Backend

This walkthrough teaches React by building a minimal UI that talks to the FastAPI backend in this repo. Follow along step-by-step; each section maps to existing backend routes and explains how the pieces fit. All frontend files referenced here live under `testAI/src/` in this repository layout.

## 0) Prerequisites
- Backend: run `make dev` (serves FastAPI on `http://localhost:8000`). Health check: `GET /healthz`.
- Node.js LTS installed. Use a separate terminal for the frontend dev server.

## 1) Create a React + TypeScript app (Vite)
```bash
npm create vite@latest studybuddy-web -- --template react-ts
cd studybuddy-web
npm install
```
Why: Vite gives a fast dev server, TypeScript for safety, and a simple file-based entry point (`src/App.tsx`).

## 2) Dev proxy to the FastAPI backend
Backend runs on 8000. Add a proxy so the web app can call API paths without CORS headaches.
```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/healthz': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/children': 'http://localhost:8000',
      '/questions': 'http://localhost:8000',
      '/attempts': 'http://localhost:8000',
      '/progress': 'http://localhost:8000',
      '/standards': 'http://localhost:8000'
    }
  }
})
```

## 3) First fetch: `GET /healthz`
Create a tiny API client and a component to render backend health.
```ts
// src/services/apiClient.ts
export async function getHealth(): Promise<string> {
  const res = await fetch('/healthz')
  if (!res.ok) throw new Error('Health check failed')
  return res.text()
}
```
```tsx
// src/App.tsx
import { useEffect, useState } from 'react'
import { getHealth } from './services/apiClient'

export default function App() {
  const [status, setStatus] = useState<string>('loading...')
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    getHealth().then(setStatus).catch((e) => setError(e.message))
  }, [])
  if (error) return <div>Backend error: {error}</div>
  return <div>Backend health: {status}</div>
}
```
Run: `npm run dev` and open the app; you should see the health string from FastAPI.

## 4) Understanding backend routes and how the UI will use them
- Auth: `POST /auth/signup`, `POST /auth/login` → returns a bearer token. UI stores it (context/state) and adds `Authorization: Bearer <token>` to protected calls.
- Children: `GET /children`, `POST /children` → list/manage child profiles.
- Questions: `POST /questions/fetch` → returns the next multiple-choice question (grade-aware). UI renders choices.
- Attempts: `POST /attempts` → submit an answer; backend records correctness and prevents repeats after correct answers.
- Progress: `GET /progress/{child_id}` → shows streaks/accuracy; UI can render a simple progress card.
- Standards: `GET /standards` → reference for Common Core-aligned standards.

Tip: Keep all HTTP calls in `src/services/apiClient.ts` so components stay focused on rendering and state.

## 5) Add routing: login → children → quiz
Install router and basic pages.
```bash
npm i react-router-dom
```
```tsx
// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/login', element: <div>Login</div> },
  { path: '/children', element: <div>Children</div> },
  { path: '/quiz/:childId', element: <div>Quiz</div> },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
```
Why: Routing lets us map pages to backend flows cleanly.

## 6) Auth flow (`POST /auth/login`)
Create a simple form and store the token.
```ts
// src/services/apiClient.ts (add)
export async function login(email: string, password: string) {
  const res = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  if (!res.ok) throw new Error('Login failed')
  return res.json() // { token: string }
}
```
```tsx
// src/context/AuthContext.tsx
import { createContext, useContext, useState } from 'react'
type Auth = { token: string | null, setToken: (t: string|null) => void }
const Ctx = createContext<Auth>({ token: null, setToken: () => {} })
export const useAuth = () => useContext(Ctx)
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string|null>(null)
  return <Ctx.Provider value={{ token, setToken }}>{children}</Ctx.Provider>
}
```
Attach token to requests:
```ts
// src/services/apiClient.ts (helper)
import { getToken } from './token'
export function authHeaders() {
  const t = getToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}
```

## 7) Children list (`GET/POST /children`)
Fetch and render a list; allow adding a child.
```ts
// src/services/apiClient.ts (add)
export async function listChildren() {
  const res = await fetch('/children', { headers: { ...authHeaders() } })
  if (!res.ok) throw new Error('Failed to load children')
  return res.json()
}
export async function addChild(payload: { name: string; grade: number }) {
  const res = await fetch('/children', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error('Failed to add child')
  return res.json()
}
```

## 8) Quiz loop (`POST /questions/fetch`, `POST /attempts`)
- Fetch the next question for a child: render prompt and choices.
- On submit, call `/attempts` with the selected choice; then refetch the next question.
- For progress, call `GET /progress/{child_id}` and show accuracy/streaks.

Key React patterns you’ll practice
- State: `useState` for local UI state; context for auth token.
- Effects: `useEffect` to fetch data on mount or when deps change.
- Composition: small reusable components (Button, Card, TextField) to keep pages clean.
- Error handling: show friendly errors; add an Error Boundary around routes.

## 9) Project hygiene
- Add ESLint/Prettier (2-space indent, ES2020).
- Add simple tests with Vitest for `apiClient` and a component render.
- Useful scripts: `npm run dev`, `npm run build`, `npm run lint`, `npm run test`.

## 10) Where this is going
- Later, move the app into this repo under `src/ui/web/` and serve built files from FastAPI.
- For iOS, we’ll reuse logic in a React Native (Expo) app and share code via a monorepo.

That’s it—you now have a path to stand up a React UI against the existing backend. Build one page at a time, verify with the dev proxy, and keep API calls in `src/services/apiClient.ts`.

---

# How the React app is organized (under `testAI/src/`)

- `testAI/src/main.tsx`: Bootstraps React. Mounts router and global providers (e.g., `AuthProvider`).
- `testAI/src/App.tsx`: Top-level layout (nav, ErrorBoundary, route outlet). Avoids direct API calls.
- `testAI/src/routes/`: Route components mapped to URLs (e.g., `Health.tsx`, `Login.tsx`, `Children.tsx`, `Quiz.tsx`). Pages orchestrate data and UI.
- `testAI/src/ui/components/`: Reusable, presentational components (`Button.tsx`, `Card.tsx`, `TextField.tsx`, `Spinner.tsx`). No side effects.
- `testAI/src/services/apiClient.ts`: Centralized HTTP helpers for backend endpoints. Attaches auth headers and parses responses.
- `testAI/src/context/AuthContext.tsx`: Holds auth token and helpers. Consumed by pages and `apiClient`.
- `testAI/src/core/theme/`: Design tokens and theming utilities consumed by components.
- `testAI/src/hooks/`: Cross-cutting hooks (e.g., `useAuth`, `useChildren`). Encapsulate fetching patterns.
- `testAI/src/types/`: Shared TypeScript types aligned with backend contracts.
- `testAI/src/lib/`: Utilities not tied to React (formatters, validators, storage).

How components work together
- Pages orchestrate data flow and navigation.
- Services (`apiClient`) handle all network IO.
- Context provides shared state (auth token) without prop drilling.
- UI components render data; they accept props and remain pure.
- Hooks wrap common fetch/state logic to keep pages slim.

Endpoint walkthroughs
1) Simple: `GET /healthz`
- Route: `testAI/src/routes/Health.tsx` uses `useEffect` to call `apiClient.getHealth()` and renders the status via a `StatusBadge` component.
- Service: `getHealth()` performs `fetch('/healthz')`, throws on failure, returns text.
- UI: `StatusBadge` renders green/amber/red based on the value.

2) Authenticated: children flows
- Login (`POST /auth/login`): `Login.tsx` posts credentials via `apiClient.login`, stores token in `AuthContext`, redirects to `/children`.
- List/Create (`GET/POST /children`): `Children.tsx` reads token from context; calls `apiClient.listChildren()` to render cards and `apiClient.addChild()` to create entries; then refetches or updates state.
- Quiz (`POST /questions/fetch`, `POST /attempts`, `GET /progress/:childId`): `Quiz.tsx` fetches the next question, posts attempts, and updates view; optionally displays progress in a sidebar using `apiClient.getProgress(childId)`.

Key patterns
- Auth propagation: `apiClient` attaches `Authorization: Bearer <token>` when present (via a small helper).
- Error handling: Services throw; pages catch and render messages. Add an ErrorBoundary at the layout level.
- State choice: Start with `useState` + `useEffect`. Consider React Query when you need caching and invalidation.

With this map, open the files under `testAI/src/` and trace the flows above. Start with the `Health` route to verify connectivity, then move on to `Login` → `Children` → `Quiz` to exercise authenticated, stateful interactions.
