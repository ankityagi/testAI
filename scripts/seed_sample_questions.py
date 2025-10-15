#!/usr/bin/env python3
"""Seed sample questions for testing"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from studybuddy.backend.db.repository import build_repository
from studybuddy.backend.services.hashing import hash_question

repo = build_repository()

# Create sample questions for Grade 3 Math Multiplication
questions = []

subtopic = "Introduction to Multiplication Facts (2s, 5s, and 10s)"

# Easy questions
easy_questions = [
    {
        "stem": "What is 2 × 3?",
        "options": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "rationale": "2 × 3 means 2 groups of 3, which equals 6."
    },
    {
        "stem": "What is 5 × 2?",
        "options": ["7", "10", "12", "15"],
        "correct_answer": "10",
        "rationale": "5 × 2 means 5 groups of 2, which equals 10."
    },
    {
        "stem": "What is 10 × 1?",
        "options": ["1", "10", "11", "20"],
        "correct_answer": "10",
        "rationale": "Any number times 1 equals that same number."
    },
    {
        "stem": "What is 2 × 5?",
        "options": ["7", "10", "12", "15"],
        "correct_answer": "10",
        "rationale": "2 × 5 means 2 groups of 5, which equals 10."
    },
    {
        "stem": "What is 5 × 1?",
        "options": ["1", "5", "6", "10"],
        "correct_answer": "5",
        "rationale": "Any number times 1 equals that same number."
    },
]

# Medium questions
medium_questions = [
    {
        "stem": "What is 5 × 4?",
        "options": ["15", "20", "25", "30"],
        "correct_answer": "20",
        "rationale": "5 × 4 means 5 groups of 4, which equals 20."
    },
    {
        "stem": "What is 10 × 3?",
        "options": ["13", "20", "30", "40"],
        "correct_answer": "30",
        "rationale": "10 × 3 means 10 groups of 3, which equals 30."
    },
    {
        "stem": "What is 2 × 8?",
        "options": ["10", "14", "16", "18"],
        "correct_answer": "16",
        "rationale": "2 × 8 means 2 groups of 8, which equals 16."
    },
    {
        "stem": "What is 5 × 5?",
        "options": ["20", "25", "30", "35"],
        "correct_answer": "25",
        "rationale": "5 × 5 means 5 groups of 5, which equals 25."
    },
    {
        "stem": "What is 10 × 5?",
        "options": ["40", "50", "60", "100"],
        "correct_answer": "50",
        "rationale": "10 × 5 means 10 groups of 5, which equals 50."
    },
]

# Hard questions
hard_questions = [
    {
        "stem": "What is 10 × 9?",
        "options": ["80", "90", "100", "110"],
        "correct_answer": "90",
        "rationale": "10 × 9 means 10 groups of 9, which equals 90."
    },
    {
        "stem": "If you have 5 bags with 7 candies in each bag, how many candies do you have in total?",
        "options": ["30", "35", "40", "45"],
        "correct_answer": "35",
        "rationale": "5 × 7 = 35 candies in total."
    },
    {
        "stem": "What is 2 × 12?",
        "options": ["20", "22", "24", "26"],
        "correct_answer": "24",
        "rationale": "2 × 12 means 2 groups of 12, which equals 24."
    },
]

# Build full question objects
for difficulty, question_list in [("easy", easy_questions), ("medium", medium_questions), ("hard", hard_questions)]:
    for q_data in question_list:
        question = {
            "id": str(uuid.uuid4()),
            "subject": "math",
            "grade": 3,
            "topic": "multiplication",
            "sub_topic": subtopic,
            "difficulty": difficulty,
            "stem": q_data["stem"],
            "options": q_data["options"],
            "correct_answer": q_data["correct_answer"],
            "rationale": q_data["rationale"],
            "source": "seeded",
            "hash": hash_question(q_data["stem"], q_data["options"], q_data["correct_answer"])
        }
        questions.append(question)

print(f"Inserting {len(questions)} sample questions...")
print(f"  Easy: {len(easy_questions)}")
print(f"  Medium: {len(medium_questions)}")
print(f"  Hard: {len(hard_questions)}")

repo.insert_questions(questions)

print(f"\n✓ Successfully inserted {len(questions)} questions")
print(f"\nVerifying...")
count = repo.count_questions(subject="math", grade=3, topic="multiplication", subtopic=subtopic)
print(f"  Database now has {count} questions for this subtopic")
