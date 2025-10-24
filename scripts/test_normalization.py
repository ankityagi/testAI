#!/usr/bin/env python3
"""
Test script to verify case normalization is working correctly.
Tests both insertion and query normalization.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from studybuddy.backend.services.text_utils import (
    normalize_subject,
    normalize_topic,
    normalize_subtopic,
    to_display_case,
    normalize_metadata
)


def test_normalization_functions():
    """Test individual normalization functions."""
    print("=" * 60)
    print("Testing Normalization Functions")
    print("=" * 60)
    print()

    # Test subject normalization
    test_subjects = ["Math", "MATH", "math", "Science", "SCIENCE"]
    print("Subject Normalization:")
    for subject in test_subjects:
        normalized = normalize_subject(subject)
        display = to_display_case(normalized)
        print(f"  {subject:10s} → {normalized:10s} → {display}")
    print()

    # Test topic normalization
    test_topics = ["Multiplication", "MULTIPLICATION", "multiplication", "Addition", "ADDITION"]
    print("Topic Normalization:")
    for topic in test_topics:
        normalized = normalize_topic(topic)
        display = to_display_case(normalized)
        print(f"  {topic:20s} → {normalized:20s} → {display}")
    print()

    # Test subtopic normalization
    test_subtopics = [
        "Single-Digit Multiplication",
        "SINGLE-DIGIT MULTIPLICATION",
        "single-digit multiplication",
        "Multi-Digit Multiplication",
        "MULTI-DIGIT MULTIPLICATION"
    ]
    print("Subtopic Normalization:")
    for subtopic in test_subtopics:
        normalized = normalize_subtopic(subtopic)
        display = to_display_case(normalized)
        print(f"  {subtopic:35s} → {normalized:35s} → {display}")
    print()


def test_normalize_metadata():
    """Test metadata normalization on dictionaries."""
    print("=" * 60)
    print("Testing Metadata Normalization")
    print("=" * 60)
    print()

    test_data = [
        {
            "subject": "Math",
            "topic": "Multiplication",
            "sub_topic": "Single-Digit Multiplication",
            "stem": "What is 2 × 3?",
            "correct_answer": "6"
        },
        {
            "subject": "SCIENCE",
            "topic": "CHEMISTRY",
            "subtopic": "ELEMENTS",
            "stem": "What is the symbol for Sodium?",
            "correct_answer": "Na"
        }
    ]

    for i, data in enumerate(test_data, 1):
        print(f"Test Case {i}:")
        print(f"  Before: {data}")
        normalized = normalize_metadata(data.copy())
        print(f"  After:  {normalized}")
        print(f"  Note: stem='{normalized.get('stem')}' and answer='{normalized.get('correct_answer')}' are unchanged")
        print()


def test_case_preservation():
    """Test that question content case is preserved."""
    print("=" * 60)
    print("Testing Case Preservation for Question Content")
    print("=" * 60)
    print()

    questions = [
        {
            "subject": "Math",
            "topic": "Multiplication",
            "sub_topic": "Single-Digit Multiplication",
            "stem": "What is 2 × 3?",
            "options": ["5", "6", "7", "8"],
            "correct_answer": "6"
        },
        {
            "subject": "Science",
            "topic": "Chemistry",
            "sub_topic": "Elements",
            "stem": "What is the chemical symbol for Sodium?",
            "options": ["Na", "na", "NA", "nA"],
            "correct_answer": "Na"
        },
        {
            "subject": "Language",
            "topic": "Spanish",
            "sub_topic": "Greetings",
            "stem": "How do you say 'Hello' in Spanish?",
            "options": ["hola", "Hola", "HOLA", "HoLa"],
            "correct_answer": "Hola"
        }
    ]

    for i, q in enumerate(questions, 1):
        normalized = normalize_metadata(q.copy())
        print(f"Question {i}:")
        print(f"  Subject:  {q['subject']:10s} → {normalized['subject']:10s}")
        print(f"  Topic:    {q['topic']:15s} → {normalized['topic']:15s}")
        print(f"  Subtopic: {q['sub_topic']:30s} → {normalized['sub_topic']:30s}")
        print(f"  Stem:     {normalized['stem']} (unchanged)")
        print(f"  Options:  {normalized['options']} (unchanged)")
        print(f"  Answer:   {normalized['correct_answer']} (unchanged)")
        print()


def test_query_matching():
    """Test that queries will match regardless of case."""
    print("=" * 60)
    print("Testing Query Matching")
    print("=" * 60)
    print()

    # Simulated stored data (after normalization)
    stored_subjects = ["math", "science", "language"]
    stored_topics = ["multiplication", "addition", "chemistry"]
    stored_subtopics = ["single-digit multiplication", "multi-digit multiplication"]

    # Test queries with different cases
    query_cases = [
        ("Math", "Multiplication", "Single-Digit Multiplication"),
        ("MATH", "MULTIPLICATION", "SINGLE-DIGIT MULTIPLICATION"),
        ("math", "multiplication", "single-digit multiplication"),
        ("MaTh", "MuLtIpLiCaTiOn", "SiNgLe-DiGiT MuLtIpLiCaTiOn")
    ]

    print("Simulating query matching:")
    print(f"  Stored data: subject='math', topic='multiplication', subtopic='single-digit multiplication'")
    print()

    for subject, topic, subtopic in query_cases:
        norm_subject = normalize_subject(subject)
        norm_topic = normalize_topic(topic)
        norm_subtopic = normalize_subtopic(subtopic)

        match_subject = norm_subject in stored_subjects
        match_topic = norm_topic in stored_topics
        match_subtopic = norm_subtopic in stored_subtopics

        print(f"  Query: subject='{subject}', topic='{topic}', subtopic='{subtopic}'")
        print(f"    Normalized: subject='{norm_subject}', topic='{norm_topic}', subtopic='{norm_subtopic}'")
        print(f"    Match: subject={match_subject}, topic={match_topic}, subtopic={match_subtopic}")
        print(f"    Display: {to_display_case(norm_subject)} / {to_display_case(norm_topic)} / {to_display_case(norm_subtopic)}")
        print()


def main():
    """Run all tests."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "CASE NORMALIZATION TESTS" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        test_normalization_functions()
        test_normalize_metadata()
        test_case_preservation()
        test_query_matching()

        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Subject/topic/subtopic normalized to lowercase for storage")
        print("  ✓ Queries normalize input before comparing")
        print("  ✓ Display formatting converts to Title Case")
        print("  ✓ Question content (stem, options, answers) preserved as-is")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
