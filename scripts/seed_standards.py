#!/usr/bin/env python3
"""Seed standards data into the database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from studybuddy.backend.db.repository import build_repository

# Grade 3 Math Standards
grade_3_standards = [
    # Operations & Algebraic Thinking
    {
        "subject": "math",
        "grade": 3,
        "domain": "Operations & Algebraic Thinking",
        "sub_domain": "Multiplication",
        "standard_ref": "CCSS.MATH.CONTENT.3.OA.A.1",
        "title": "Multiplication as repeated addition",
        "description": "Interpret products of whole numbers as the total number of objects in equal groups."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Operations & Algebraic Thinking",
        "sub_domain": "Division",
        "standard_ref": "CCSS.MATH.CONTENT.3.OA.A.2",
        "title": "Division as equal shares",
        "description": "Interpret whole-number quotients of whole numbers."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Operations & Algebraic Thinking",
        "sub_domain": "Multiplication",
        "standard_ref": "CCSS.MATH.CONTENT.3.OA.C.7",
        "title": "Multiply and divide within 100",
        "description": "Fluently multiply and divide within 100, using strategies such as the relationship between multiplication and division."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Operations & Algebraic Thinking",
        "sub_domain": "Patterns",
        "standard_ref": "CCSS.MATH.CONTENT.3.OA.D.9",
        "title": "Identify arithmetic patterns",
        "description": "Identify arithmetic patterns including patterns in the addition table or multiplication table."
    },

    # Number & Operations in Base Ten
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations in Base Ten",
        "sub_domain": "Place Value",
        "standard_ref": "CCSS.MATH.CONTENT.3.NBT.A.1",
        "title": "Understand place value",
        "description": "Use place value understanding to round whole numbers to the nearest 10 or 100."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations in Base Ten",
        "sub_domain": "Addition",
        "standard_ref": "CCSS.MATH.CONTENT.3.NBT.A.2",
        "title": "Add and subtract within 1000",
        "description": "Fluently add and subtract within 1000 using strategies and algorithms."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations in Base Ten",
        "sub_domain": "Multiplication",
        "standard_ref": "CCSS.MATH.CONTENT.3.NBT.A.3",
        "title": "Multiply one-digit numbers",
        "description": "Multiply one-digit whole numbers by multiples of 10 in the range 10-90."
    },

    # Number & Operations - Fractions
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations - Fractions",
        "sub_domain": "Understanding Fractions",
        "standard_ref": "CCSS.MATH.CONTENT.3.NF.A.1",
        "title": "Understand fractions as numbers",
        "description": "Understand a fraction 1/b as the quantity formed by 1 part when a whole is partitioned into b equal parts."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations - Fractions",
        "sub_domain": "Number Line",
        "standard_ref": "CCSS.MATH.CONTENT.3.NF.A.2",
        "title": "Represent fractions on a number line",
        "description": "Represent a fraction on a number line diagram."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Number & Operations - Fractions",
        "sub_domain": "Equivalence",
        "standard_ref": "CCSS.MATH.CONTENT.3.NF.A.3",
        "title": "Explain fraction equivalence",
        "description": "Explain equivalence of fractions and compare fractions by reasoning about their size."
    },

    # Measurement & Data
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Time",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.A.1",
        "title": "Tell and write time",
        "description": "Tell and write time to the nearest minute and measure time intervals in minutes."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Volume and Mass",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.A.2",
        "title": "Measure volume and mass",
        "description": "Measure and estimate liquid volumes and masses of objects using standard units."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Data",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.B.3",
        "title": "Draw and interpret graphs",
        "description": "Draw a scaled picture graph and a scaled bar graph to represent a data set."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Measurement",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.B.4",
        "title": "Measure lengths and area",
        "description": "Generate measurement data by measuring lengths using rulers marked with halves and fourths of an inch."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Area",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.C.5",
        "title": "Understand area concepts",
        "description": "Recognize area as an attribute of plane figures and understand concepts of area measurement."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Measurement & Data",
        "sub_domain": "Perimeter",
        "standard_ref": "CCSS.MATH.CONTENT.3.MD.D.8",
        "title": "Solve perimeter problems",
        "description": "Solve real world problems involving perimeters of polygons."
    },

    # Geometry
    {
        "subject": "math",
        "grade": 3,
        "domain": "Geometry",
        "sub_domain": "Shapes",
        "standard_ref": "CCSS.MATH.CONTENT.3.G.A.1",
        "title": "Understand categories of shapes",
        "description": "Understand that shapes in different categories may share attributes."
    },
    {
        "subject": "math",
        "grade": 3,
        "domain": "Geometry",
        "sub_domain": "Partitioning",
        "standard_ref": "CCSS.MATH.CONTENT.3.G.A.2",
        "title": "Partition shapes into equal areas",
        "description": "Partition shapes into parts with equal areas and express the area as a unit fraction."
    }
]

def main():
    """Insert grade 3 standards into database"""
    print(f"Connecting to database...")
    repo = build_repository()

    print(f"Inserting {len(grade_3_standards)} grade 3 math standards...")

    for std in grade_3_standards:
        try:
            repo.insert_standard(**std)
            print(f"  ✓ {std['standard_ref']}: {std['title']}")
        except Exception as e:
            print(f"  ✗ {std['standard_ref']}: {e}")

    print("\n✓ Grade 3 standards seeded successfully!")

    # Verify
    all_standards = repo.list_standards()
    grade_3_count = len([s for s in all_standards if s.get('grade') == 3])
    print(f"\nTotal standards in database: {len(all_standards)}")
    print(f"Grade 3 standards: {grade_3_count}")

    # Show domains
    grade_3_domains = set(s.get('domain') for s in all_standards if s.get('grade') == 3)
    print(f"Grade 3 domains: {sorted(grade_3_domains)}")

if __name__ == "__main__":
    main()
