#!/usr/bin/env python3
"""Delete mock questions from the database."""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_connection():
    url = os.environ.get("SUPABASE_URL")
    password = os.environ.get("SUPABASE_DB_PASSWORD")

    if not url or not password:
        raise RuntimeError("SUPABASE_URL and SUPABASE_DB_PASSWORD must be set")

    host = url.replace("https://", "").replace("http://", "").split("/")[0]
    project_ref = host.split(".")[0]

    conn_params = {
        "host": "aws-1-us-west-1.pooler.supabase.com",
        "port": 6543,
        "database": "postgres",
        "user": f"postgres.{project_ref}",
        "password": password,
    }

    return psycopg2.connect(**conn_params)

def main():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Count mock questions before deletion
            cur.execute("SELECT COUNT(*) FROM question_bank WHERE source = 'mock'")
            count_before = cur.fetchone()[0]
            print(f"Found {count_before} mock questions in database")

            if count_before == 0:
                print("No mock questions to delete")
                return

            # Delete mock questions
            cur.execute("DELETE FROM question_bank WHERE source = 'mock'")
            conn.commit()

            # Count after deletion
            cur.execute("SELECT COUNT(*) FROM question_bank WHERE source = 'mock'")
            count_after = cur.fetchone()[0]

            print(f"Deleted {count_before - count_after} mock questions")
            print(f"Remaining mock questions: {count_after}")

            # Show remaining question counts by source
            cur.execute("SELECT source, COUNT(*) FROM question_bank GROUP BY source")
            print("\nRemaining questions by source:")
            for row in cur.fetchall():
                print(f"  {row[0]}: {row[1]}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
