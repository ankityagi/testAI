#!/bin/bash

# Run case normalization migration on Supabase database
# This script normalizes subject/topic/subtopic to lowercase across all tables

set -e  # Exit on error

echo "==========================================="
echo "Case Normalization Migration"
echo "==========================================="
echo ""

# Check required environment variables
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ Error: SUPABASE_URL not set"
    echo "Please set SUPABASE_URL in your .env file"
    exit 1
fi

if [ -z "$SUPABASE_DB_PASSWORD" ]; then
    echo "❌ Error: SUPABASE_DB_PASSWORD not set"
    echo "Please set SUPABASE_DB_PASSWORD in your .env file"
    exit 1
fi

# Extract project reference from URL
PROJECT_REF=$(echo $SUPABASE_URL | sed 's|https://||' | sed 's|http://||' | cut -d'.' -f1)

echo "📊 Database: $PROJECT_REF"
echo "📝 Migration: Normalize subject/topic/subtopic to lowercase"
echo ""

# Confirm before running
read -p "⚠️  This will modify existing data. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Migration cancelled"
    exit 0
fi

echo ""
echo "🔄 Running migration..."
echo ""

# Run migration SQL
PGPASSWORD=$SUPABASE_DB_PASSWORD psql \
    -h aws-1-us-west-1.pooler.supabase.com \
    -p 6543 \
    -U postgres.$PROJECT_REF \
    -d postgres \
    -f studybuddy/backend/db/sql/migration_normalize_case.sql

echo ""
echo "✅ Migration completed successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Verify data looks correct in Supabase SQL Editor"
echo "  2. Test question picker with OpenAI-generated questions"
echo "  3. Verify UI displays Title Case formatting correctly"
echo ""
