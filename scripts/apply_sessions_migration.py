#!/usr/bin/env python3
"""
Apply sessions table migration to database.
"""
import os
import sys
from pathlib import Path

import psycopg2

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Apply the sessions migration."""
    migration_file = Path(__file__).parent.parent / "studybuddy" / "backend" / "db" / "sql" / "migration_add_sessions.sql"

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        sys.exit(1)

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

    print("🔄 Applying sessions table migration...")
    print(f"  Host: {conn_params['host']}")
    print(f"  User: {conn_params['user']}")

    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Read migration SQL
        with migration_file.open("r", encoding="utf-8") as f:
            sql = f.read()

        print(f"\n📝 Applying migration from: {migration_file.name}")
        cursor.execute(sql)
        conn.commit()

        print("✅ Migration applied successfully!")

        # Verify table was created
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions')")
        exists = cursor.fetchone()[0]

        if exists:
            print("✅ Sessions table exists")

            # Check indexes
            cursor.execute("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'sessions'
                ORDER BY indexname
            """)
            indexes = cursor.fetchall()
            print(f"✅ {len(indexes)} indexes created:")
            for idx in indexes:
                print(f"   - {idx[0]}")
        else:
            print("❌ Sessions table was not created")
            sys.exit(1)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
