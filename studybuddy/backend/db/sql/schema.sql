create extension if not exists "uuid-ossp";

create table parents (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  password_hash text not null,
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

create table parent_tokens (
  token text primary key,
  parent_id uuid references parents(id) on delete cascade,
  created_at timestamptz default now()
);

create table pacing_presets (
  id serial primary key,
  grade int,
  month int,
  subject text,
  topics jsonb
);

create table subtopics (
  id uuid primary key default uuid_generate_v4(),
  subject text not null,
  grade int not null,
  topic text not null,
  subtopic text not null,
  description text,
  sequence_order int,
  created_at timestamptz default now(),
  unique(subject, grade, topic, subtopic)
);

create index if not exists idx_attempts_child_created on attempts(child_id, created_at desc);
create index if not exists idx_question_bank_standard on question_bank(standard_ref);
create index if not exists idx_subtopics_lookup on subtopics(subject, grade, topic);
create index if not exists idx_question_bank_subtopic on question_bank(subject, grade, topic, sub_topic);
