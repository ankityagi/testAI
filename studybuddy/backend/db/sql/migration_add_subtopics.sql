-- Migration: Add subtopics table
-- Run this to add the subtopics table to an existing database

create table if not exists subtopics (
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

create index if not exists idx_subtopics_lookup on subtopics(subject, grade, topic);
create index if not exists idx_question_bank_subtopic on question_bank(subject, grade, topic, sub_topic);
