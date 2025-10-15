#!/usr/bin/env python3
"""
Update seed questions with proper subtopics from subtopics table.
Maps existing generic sub_topic values to real subtopic names.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from studybuddy.backend.db.repository import build_repository


def load_seed_questions():
    """Load seed questions from JSON file."""
    seed_file = Path(__file__).parent.parent / "studybuddy" / "backend" / "db" / "sql" / "seed_questions.json"

    if not seed_file.exists():
        print(f"ERROR: Seed questions file not found: {seed_file}")
        sys.exit(1)

    with seed_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def map_question_to_subtopic(repo, question):
    """
    Map a seed question to an appropriate subtopic from the subtopics table.

    Strategy:
    1. Get all subtopics for this subject/grade/topic
    2. Find the best match based on the question's sub_topic field
    3. If no good match, use the first subtopic (sequence_order = 1)
    """
    subject = question["subject"]
    grade = question["grade"]
    topic = question["topic"]
    current_subtopic = question.get("sub_topic", "")

    # Get all subtopics for this combination
    subtopics = repo.list_subtopics(subject=subject, grade=grade, topic=topic)

    if not subtopics:
        print(f"WARNING: No subtopics found for {subject}/{grade}/{topic}")
        return current_subtopic  # Keep existing

    # Try to find a fuzzy match
    current_lower = current_subtopic.lower()
    for st in subtopics:
        st_name = st["subtopic"]
        st_desc = st.get("description", "")

        # Check for keyword matches
        if current_lower in st_name.lower() or st_name.lower() in current_lower:
            print(f"  Matched '{current_subtopic}' → '{st_name}'")
            return st_name

        # Check description
        if current_lower in st_desc.lower():
            print(f"  Matched via description '{current_subtopic}' → '{st_name}'")
            return st_name

    # No match found - use the first subtopic (lowest sequence_order)
    first_subtopic = min(subtopics, key=lambda x: x.get("sequence_order", 999))
    print(f"  No match for '{current_subtopic}', using first: '{first_subtopic['subtopic']}'")
    return first_subtopic["subtopic"]


def update_questions_with_subtopics(repo, questions):
    """Update each question with proper subtopic."""
    updated_questions = []

    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {question['subject']} Grade {question['grade']} - {question['topic']}")

        # Map to real subtopic
        new_subtopic = map_question_to_subtopic(repo, question)

        # Update the question
        updated_question = question.copy()
        updated_question["sub_topic"] = new_subtopic
        updated_questions.append(updated_question)

    return updated_questions


def save_updated_questions(questions):
    """Save updated questions back to JSON file."""
    seed_file = Path(__file__).parent.parent / "studybuddy" / "backend" / "db" / "sql" / "seed_questions.json"

    print(f"\n✓ Saving {len(questions)} updated questions to {seed_file.name}")
    with seed_file.open("w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


def load_into_database(repo, questions):
    """Load seed questions into database."""
    print(f"\n✓ Loading {len(questions)} questions into database...")

    # Add hash if not present
    for question in questions:
        if "hash" not in question:
            from studybuddy.backend.services.hashing import hash_question
            question["hash"] = hash_question(
                question["stem"],
                question["options"],
                question["correct_answer"]
            )

    # Insert all questions at once
    try:
        repo.insert_questions(questions)  # Use plural method
        print(f"✓ {len(questions)} questions loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to insert questions: {e}")
        raise


def main():
    """Main function."""
    print("=== Update Seed Questions with Subtopics ===\n")

    # Connect to database
    print("[1] Connecting to database...")
    repo = build_repository()

    # Check subtopics exist
    math_count = repo.count_subtopics(subject="math")
    reading_count = repo.count_subtopics(subject="reading")
    print(f"    Found {math_count} math subtopics, {reading_count} reading subtopics")

    if math_count == 0 and reading_count == 0:
        print("\nERROR: No subtopics found in database!")
        print("Run './scripts/run_seed_subtopics.sh' first to load subtopics.")
        sys.exit(1)

    # Load seed questions
    print("\n[2] Loading seed questions...")
    questions = load_seed_questions()
    print(f"    Loaded {len(questions)} seed questions")

    # Update with proper subtopics
    print("\n[3] Mapping questions to subtopics...")
    updated_questions = update_questions_with_subtopics(repo, questions)

    # Save back to file
    print("\n[4] Saving updated questions...")
    save_updated_questions(updated_questions)

    # Load into database
    print("\n[5] Loading into database...")
    load_into_database(repo, updated_questions)

    # Verify
    print("\n[6] Verification...")

    # Count by subject
    math_questions = repo.count_questions(subject="math")
    reading_questions = repo.count_questions(subject="reading")
    print(f"    Total questions in database:")
    print(f"      Math: {math_questions}")
    print(f"      Reading: {reading_questions}")

    # Show sample subtopics used
    print("\n    Sample questions by subtopic:")
    for q in updated_questions[:5]:
        print(f"      {q['subject']}/{q['topic']}/{q['sub_topic']}")

    print("\n=== ✓ Seed Questions Updated Successfully ===")


if __name__ == "__main__":
    main()
