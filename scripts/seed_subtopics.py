#!/usr/bin/env python3
"""
Load subtopic seed data from JSON file into the database.
Run this after generating seed_subtopics.json with generate_subtopic_seeds.py
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import from studybuddy
sys.path.insert(0, str(Path(__file__).parent.parent))

from studybuddy.backend.db.repository import build_repository


def main():
    """Load subtopics from seed file into database."""
    seed_file = Path(__file__).parent.parent / "studybuddy" / "backend" / "db" / "sql" / "seed_subtopics.json"

    if not seed_file.exists():
        print(f"ERROR: Seed file not found: {seed_file}")
        print("Run scripts/generate_subtopic_seeds.py first to generate the seed data.")
        sys.exit(1)

    # Check for database connection settings
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_DB_PASSWORD"):
        print("ERROR: Database connection not configured")
        print("Set SUPABASE_URL and SUPABASE_DB_PASSWORD environment variables")
        sys.exit(1)

    # Load subtopics from file
    print(f"Loading subtopics from: {seed_file}")
    with seed_file.open("r", encoding="utf-8") as f:
        subtopics = json.load(f)

    print(f"Found {len(subtopics)} subtopics in seed file")

    # Build repository and insert
    print("\nConnecting to database...")
    repo = build_repository()

    print("Inserting subtopics into database...")
    repo.insert_subtopics(subtopics)

    print(f"\n✓ Successfully loaded {len(subtopics)} subtopics into database")

    # Verify by counting
    print("\nVerifying by subject:")
    for subject in ["math", "reading"]:
        count = repo.count_subtopics(subject=subject)
        print(f"  {subject}: {count} subtopics")


if __name__ == "__main__":
    main()
