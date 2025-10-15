#!/usr/bin/env python3
"""Check question inventory for debugging"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from studybuddy.backend.db.repository import build_repository

repo = build_repository()

print("=" * 70)
print("Question Inventory Check")
print("=" * 70)

# Check the specific subtopic from the logs
child_id = "0c3e8dad-9296-4b79-bc68-f8e855ffb68e"  # From logs
subject = "math"
grade = 3
topic = "multiplication"
subtopic = "Introduction to Multiplication Facts (2s, 5s, and 10s)"

print(f"\n1. Total questions in database:")
total = repo.count_questions(subject=subject, grade=grade, topic=topic, subtopic=subtopic)
print(f"   {subject} / Grade {grade} / {topic} / {subtopic}: {total} questions")

print(f"\n2. Checking seen questions for child {child_id}:")
seen_hashes = list(repo.list_seen_question_hashes(child_id))
print(f"   Child has seen {len(seen_hashes)} questions")

print(f"\n3. Available (unseen) questions:")
all_questions = repo.list_questions(
    subject=subject,
    grade=grade,
    topic=topic,
    subtopic=subtopic
)
print(f"   Total questions for subtopic: {len(all_questions)}")

seen_set = set(seen_hashes)
unseen = [q for q in all_questions if q["hash"] not in seen_set]
print(f"   Unseen questions: {len(unseen)}")

if unseen:
    print(f"\n4. Sample unseen questions:")
    for i, q in enumerate(unseen[:3], 1):
        print(f"   {i}. [{q.get('difficulty', 'unknown')}] {q.get('stem', '')[:80]}...")
else:
    print(f"\n4. No unseen questions available!")
    print(f"\n5. All questions (seen and unseen):")
    for i, q in enumerate(all_questions[:5], 1):
        is_seen = "SEEN" if q["hash"] in seen_set else "NEW"
        print(f"   {i}. [{is_seen}] [{q.get('difficulty', 'unknown')}] {q.get('stem', '')[:80]}...")

print(f"\n6. Checking if questions are being generated:")
print(f"   If unseen = 0, AI should generate new questions on next fetch")
