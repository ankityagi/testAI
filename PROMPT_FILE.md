You are Codex, tasked with generating a complete, runnable POC called "studybuddy" for parents to help kids practice school quizzes/tests.  

Stack: FastAPI backend, Supabase (Auth + Postgres), and pure HTML/JS frontend. Deploy on a single Render VM. Deliver production-sane POC code with clear README and seed data.

---

## High-level requirements
- Parents sign up with email/password (Supabase Auth), create children profiles (name, age or grade, ZIP).
- OpenAI integration for generating trivia questions
- Use age+ZIP to suggest topics likely taught now (Common Core pacing heuristic). Parents can override.
- Generate/serve multiple-choice questions (MCQs) for Math and Reading, mapped to CCSS standards.
- Start with seed questions for grades K-5 and then generate async more as the user goes through them
- Guarantee "new questions" (no repeats per child) if they got it right. Persist all attempts with correctness. 
- The questions to get gradually harder as they progress and get more correct answers.
- Keep it minimal, dependency-light, and secure-by-default (RLS in Supabase; server-only secrets).
- Serve static frontend from the FastAPI app.

---
## API Endpoints
GET /children → list
POST /children → create
POST /questions/fetch → fetch 5 unseen questions
POST /attempts → submit attempt, return correctness
GET /progress/{child_id} → aggregate accuracy
GET /standards → list standards by grade/subject
POST /admin/generate → pre-generate questions (admin only)
GET /healthz

---
### Front End Pages
- Login
- Welcome parent - setup child profiles / select profile already created
- Welcome child page - select category ('math', 'reading', 'science') and sub_category ('fraction', 'random', etc.)
- Quiz page where the child attemps the questions and selects answer before moving to next page/question show them if what they selected was correct or not
- Good bye page to show the current streak and overall metrics in a graph that show what areas they need to work on more and where they are good already
- All pages to have responsive design and attarctive fun and modern theme



---
### Backend services
pacing.py: suggest topics by grade+month.
hashing.py: stable hash for stem+options+answer.
validators.py: ensure 4 options, 1 correct, no duplicates.
genai.py: call LLM with system+user prompt, output JSON MCQs, validate, hash, dedupe.
question_picker.py: fetch unseen questions, top up with genai if needed.

---

## Repository layout
studybuddy/
- backend/
  - app.py (FastAPI entry)
  - deps.py (DB, auth helpers)
  - models.py (Pydantic schemas)
  - routes/
    - auth.py
    - children.py
    - standards.py
    - questions.py
    - attempts.py
    - progress.py
    - admin.py
    - health.py
  - services/
    - pacing.py
    - question_picker.py
    - genai.py
    - hashing.py
    - validators.py
  - db/
    - supabase_client.py
    - sql/
      - schema.sql
      - policies.sql
      - seed_standards.sql
      - seed_questions.json
      - seed_pacing.json
  - static/
    - index.html
    - styles.css
    - js/
      - auth.js
      - api.js
      - children.js
      - practice.js
      - history.js
- render.yaml
- Dockerfile
- .env.example
- README.md

## General Instructions
- Use environment variables for secrets and URLs
- Ensure CORS is configured for frontend-backend communication
- Provide clear error handling and user feedback
- Write clean, maintainable, and well-documented code

---

## Database schema (schema.sql)
```sql
create table parents (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  created_at timestamptz default now()
);

create table children (
  id uuid primary key default uuid_generate_v4(),
  parent_id uuid references parents(id) on delete cascade,
  name text not null,
  birthdate date,
  grade int,
  zip text,
  created_at timestamptz default now()
);

create table standards (
  id serial primary key,
  subject text not null,
  grade int not null,
  domain text,
  sub_domain text,
  standard_ref text unique not null,
  title text,
  description text
);

create table question_bank (
  id uuid primary key default uuid_generate_v4(),
  standard_ref text references standards(standard_ref),
  subject text,
  grade int,
  topic text,
  sub_topic text,
  difficulty text,
  stem text,
  options jsonb,
  correct_answer text,
  rationale text,
  source text,
  image BYTEA,
  hash text unique,
  created_at timestamptz default now()
);

create table attempts (
  id uuid primary key default uuid_generate_v4(),
  child_id uuid references children(id) on delete cascade,
  question_id uuid references question_bank(id),
  selected text,
  correct boolean,
  time_spent_ms int,
  created_at timestamptz default now()
);

create table seen_questions (
  child_id uuid references children(id) on delete cascade,
  question_hash text,
  first_seen_at timestamptz default now(),
  primary key(child_id, question_hash)
);

create table pacing_presets (
  id serial primary key,
  grade int,
  month int,
  subject text,
  topics jsonb
);

create index idx_attempts_child_created on attempts(child_id, created_at desc);
create index idx_question_bank_standard on question_bank(standard_ref);
