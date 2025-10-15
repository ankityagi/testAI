#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$')
fi

# Make sure we're using supabase mode
export STUDYBUDDY_DATA_MODE=supabase

# Activate virtual environment
source testai-env/bin/activate

# Run the seed script
python3 scripts/seed_sample_questions.py
