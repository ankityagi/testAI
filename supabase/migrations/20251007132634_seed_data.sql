-- Seed standards data
insert into standards (subject, grade, domain, sub_domain, standard_ref, title, description) values
  ('math', 1, 'Operations & Algebraic Thinking', 'Addition', 'CCSS.MATH.CONTENT.1.OA.C.6', 'Add and subtract within 20.', 'Fluently add and subtract within 20 using strategies.'),
  ('reading', 1, 'Key Ideas and Details', 'Comprehension', 'CCSS.ELA-LITERACY.RL.1.2', 'Retell stories', 'Retell stories, including key details, and demonstrate understanding of their central message.');

-- Seed question bank data
INSERT INTO question_bank (standard_ref, subject, grade, topic, sub_topic, difficulty, stem, options, correct_answer, rationale, source, hash) VALUES
(
  'CCSS.MATH.CONTENT.1.OA.C.6',
  'math',
  1,
  'addition',
  'within 20',
  'easy',
  'What is 8 + 7?',
  '["13", "14", "15", "16"]'::jsonb,
  '15',
  'Add 8 and 7 to get 15.',
  'seed',
  md5('What is 8 + 7?13141516')
),
(
  'CCSS.MATH.CONTENT.1.OA.C.6',
  'math',
  1,
  'addition',
  'within 20',
  'medium',
  'Liam has 9 marbles and finds 7 more. How many marbles does he have now?',
  '["15", "16", "17", "18"]'::jsonb,
  '16',
  '9 + 7 = 16.',
  'seed',
  md5('Liam has 9 marbles and finds 7 more. How many marbles does he have now?15161718')
),
(
  'CCSS.ELA-LITERACY.RL.1.2',
  'reading',
  1,
  'comprehension',
  'retell',
  'easy',
  'What do you call the main idea of a story?',
  '["The chapter", "The title", "The setting", "The message"]'::jsonb,
  'The message',
  'The main idea tells the message of the story.',
  'seed',
  md5('What do you call the main idea of a story?The chapterThe titleThe settingThe message')
);

-- Seed pacing presets
INSERT INTO pacing_presets (grade, month, subject, topics) VALUES
(
  1,
  9,
  'math',
  '["addition within 10", "shapes"]'::jsonb
),
(
  1,
  9,
  'reading',
  '["sight words", "simple sentences"]'::jsonb
);
