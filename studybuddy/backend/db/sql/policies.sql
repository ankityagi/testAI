-- Row Level Security policies will be refined in later phases.
-- Enable RLS on relevant tables and add minimal stubs for local testing.

alter table parents enable row level security;
alter table children enable row level security;
alter table question_bank enable row level security;
alter table attempts enable row level security;
alter table seen_questions enable row level security;
alter table parent_tokens enable row level security;

create policy "Parents manage own profile" on parents
  for select using (auth.uid() = id);

create policy "Parents manage own children" on children
  for all using (auth.uid() = parent_id)
  with check (auth.uid() = parent_id);

create policy "Parents view question bank" on question_bank
  for select using (true);

create policy "Parents track attempts" on attempts
  for all using (auth.uid() = (
    select parent_id from children where children.id = attempts.child_id
  ));

create policy "Parents track seen questions" on seen_questions
  for all using (auth.uid() = (
    select parent_id from children where children.id = seen_questions.child_id
  ));

create policy "Parents own tokens" on parent_tokens
  for all using (auth.uid() = parent_id);
