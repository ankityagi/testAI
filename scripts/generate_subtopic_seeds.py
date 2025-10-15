#!/usr/bin/env python3
"""
One-time script to generate subtopic seed data for all grades K-12.
Run this once to create studybuddy/backend/db/sql/seed_subtopics.json
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuration
GRADES = list(range(0, 13))  # K-12 (0 = Kindergarten)
SUBJECTS = ["math", "reading"]

# Topic definitions per grade/subject
# Expanded based on Common Core standards
TOPICS_BY_GRADE_SUBJECT = {
    "math": {
        0: ["counting", "shapes", "patterns", "measurement"],
        1: ["addition", "subtraction", "place value", "measurement", "time"],
        2: ["addition", "subtraction", "place value", "time", "money", "measurement"],
        3: ["multiplication", "division", "fractions", "geometry", "measurement"],
        4: ["multiplication", "division", "fractions", "decimals", "geometry"],
        5: ["fractions", "decimals", "volume", "coordinate plane", "expressions"],
        6: ["ratios", "expressions", "equations", "geometry", "statistics"],
        7: ["ratios", "proportions", "integers", "expressions", "equations", "geometry", "probability"],
        8: ["linear equations", "functions", "geometry", "pythagorean theorem", "statistics"],
        9: ["algebra", "functions", "linear equations", "exponential functions", "geometry"],
        10: ["geometry", "trigonometry", "coordinate geometry", "proofs"],
        11: ["algebra 2", "quadratic functions", "polynomials", "rational expressions", "logarithms"],
        12: ["precalculus", "trigonometry", "limits", "sequences", "series"],
    },
    "reading": {
        0: ["phonics", "sight words", "comprehension", "vocabulary"],
        1: ["phonics", "comprehension", "retell", "vocabulary", "main idea"],
        2: ["fluency", "comprehension", "inference", "vocabulary", "text features"],
        3: ["comprehension", "inference", "theme", "vocabulary", "author's purpose"],
        4: ["comprehension", "inference", "theme", "point of view", "text structure"],
        5: ["comprehension", "theme", "summarizing", "comparing texts", "figurative language"],
        6: ["literary analysis", "theme", "text structure", "author's purpose", "argument"],
        7: ["literary analysis", "theme", "inference", "textual evidence", "argument"],
        8: ["literary analysis", "argument", "rhetoric", "textual evidence", "writing"],
        9: ["literature", "rhetoric", "analysis", "argument", "research"],
        10: ["literature", "rhetoric", "analysis", "synthesis", "research"],
        11: ["literature", "literary theory", "rhetoric", "analysis", "research"],
        12: ["literature", "critical analysis", "rhetoric", "synthesis", "research"],
    }
}


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def generate_subtopics_for_topic(
    grade: int,
    subject: str,
    topic: str
) -> list[dict[str, Any]]:
    """Generate subtopics for a specific grade/subject/topic using OpenAI."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    grade_text = "Kindergarten" if grade == 0 else f"Grade {grade}"

    prompt = f"""For {grade_text} {subject}, generate a comprehensive list of subtopics for the topic "{topic}".

Each subtopic should:
- Be aligned with Common Core, Eureka Math or relevant educational standards for {grade_text}
- Be specific and measurable
- Follow a logical learning progression from simple to complex
- Include a brief description (1-2 sentences) explaining what students will learn

Respond with a JSON object in this exact format:
{{
  "subtopics": [
    {{
      "subtopic": "name of subtopic",
      "description": "what students will learn in 1-2 sentences",
      "sequence_order": 1
    }}
  ]
}}

Generate 5-10 subtopics per topic, ordered from foundational concepts to advanced applications.
Make sure subtopics are age-appropriate for {grade_text} students."""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "You are an expert curriculum designer creating Common Core-aligned subtopics for K-12 education."
            },
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    data = json.loads(response.choices[0].message.content)
    subtopics = data.get("subtopics", [])

    # Add metadata
    for st in subtopics:
        st["subject"] = subject
        st["grade"] = grade
        st["topic"] = topic

    return subtopics


def main():
    """Generate all subtopics and save to seed file."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    all_subtopics = []
    total_api_calls = 0

    print("=" * 70)
    print("Subtopic Seed Generation Script")
    print("=" * 70)
    print(f"Generating subtopics for grades K-12")
    print(f"Subjects: {', '.join(SUBJECTS)}")
    print(f"Output: studybuddy/backend/db/sql/seed_subtopics.json")
    print("=" * 70)

    for subject in SUBJECTS:
        print(f"\n{'='*70}")
        print(f"SUBJECT: {subject.upper()}")
        print(f"{'='*70}")

        for grade in GRADES:
            topics = TOPICS_BY_GRADE_SUBJECT.get(subject, {}).get(grade, [])

            if not topics:
                print(f"  Grade {grade}: No topics defined, skipping")
                continue

            grade_text = "K" if grade == 0 else str(grade)
            print(f"\n  Grade {grade_text}: {len(topics)} topics")

            for topic in topics:
                print(f"    • {topic}... ", end="", flush=True)
                try:
                    subtopics = generate_subtopics_for_topic(grade, subject, topic)
                    all_subtopics.extend(subtopics)
                    total_api_calls += 1
                    print(f"✓ ({len(subtopics)} subtopics)")

                    # Rate limiting: small delay between calls
                    time.sleep(0.5)

                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue

    # Save to seed file
    output_dir = Path("studybuddy/backend/db/sql")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "seed_subtopics.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_subtopics, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Total subtopics generated: {len(all_subtopics)}")
    print(f"✓ Total OpenAI API calls: {total_api_calls}")
    print(f"✓ Saved to: {output_path}")
    print("\nNext steps:")
    print("1. Review the generated subtopics in the JSON file")
    print("2. Edit/curate as needed")
    print("3. Run database seed script to populate subtopics table")
    print("=" * 70)


if __name__ == "__main__":
    main()
