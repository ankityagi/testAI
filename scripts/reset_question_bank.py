#!/usr/bin/env python3
"""
Reset question bank for subtopic implementation.
Clears question_bank, attempts, and seen_questions tables.
"""
import os
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Reset question bank tables."""
    print("=== Reset Question Bank ===\n")

    # Check for database connection settings
    url = os.getenv("SUPABASE_URL")
    password = os.getenv("SUPABASE_DB_PASSWORD")

    if not url or not password:
        print("ERROR: Database connection not configured")
        print("Set SUPABASE_URL and SUPABASE_DB_PASSWORD environment variables")
        sys.exit(1)

    # Parse connection details
    host = url.replace("https://", "").replace("http://", "").split("/")[0]
    project_ref = host.split(".")[0]

    conn_params = {
        "host": "aws-1-us-west-1.pooler.supabase.com",
        "port": 6543,
        "database": "postgres",
        "user": f"postgres.{project_ref}",
        "password": password,
    }

    print("⚠️  WARNING: This will delete ALL questions, attempts, and seen_questions!")
    print("\nThis is acceptable for development, but would require a migration strategy in production.")
    print("\nAfter truncation:")
    print("  - Questions will be regenerated on-demand with subtopic context")
    print("  - All user progress will be reset")

    confirm = input("\nAre you sure you want to continue? (yes/no): ")

    if confirm.lower() != "yes":
        print("\n✗ Cancelled - no changes made")
        sys.exit(0)

    print("\nConnecting to database...")
    print(f"  Host: {conn_params['host']}")
    print(f"  User: {conn_params['user']}")

    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get counts before truncation
        print("\n[1] Current state:")
        cursor.execute("SELECT COUNT(*) as count FROM question_bank")
        question_count = cursor.fetchone()["count"]
        print(f"    question_bank: {question_count} records")

        cursor.execute("SELECT COUNT(*) as count FROM attempts")
        attempts_count = cursor.fetchone()["count"]
        print(f"    attempts: {attempts_count} records")

        cursor.execute("SELECT COUNT(*) as count FROM seen_questions")
        seen_count = cursor.fetchone()["count"]
        print(f"    seen_questions: {seen_count} records")

        # Truncate tables
        print("\n[2] Truncating tables...")
        cursor.execute("TRUNCATE TABLE question_bank CASCADE")
        print("    ✓ question_bank truncated")

        cursor.execute("TRUNCATE TABLE attempts CASCADE")
        print("    ✓ attempts truncated")

        cursor.execute("TRUNCATE TABLE seen_questions CASCADE")
        print("    ✓ seen_questions truncated")

        conn.commit()

        # Verify empty state
        print("\n[3] Verifying empty state...")
        cursor.execute("SELECT COUNT(*) as count FROM question_bank")
        question_count = cursor.fetchone()["count"]
        assert question_count == 0, "question_bank should be empty"
        print(f"    ✓ question_bank: {question_count} records")

        cursor.execute("SELECT COUNT(*) as count FROM attempts")
        attempts_count = cursor.fetchone()["count"]
        assert attempts_count == 0, "attempts should be empty"
        print(f"    ✓ attempts: {attempts_count} records")

        cursor.execute("SELECT COUNT(*) as count FROM seen_questions")
        seen_count = cursor.fetchone()["count"]
        assert seen_count == 0, "seen_questions should be empty"
        print(f"    ✓ seen_questions: {seen_count} records")

        cursor.close()
        conn.close()

        print("\n=== ✓ Question Bank Reset Complete ===")
        print("\nQuestions will be regenerated with subtopics on-demand when users request them.")

    except Exception as e:
        print(f"\n✗ Reset failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
