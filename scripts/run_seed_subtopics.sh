#!/bin/bash
# Wrapper script to run subtopic seeding with proper environment

# Load environment variables
set -a
source .env
set +a

# Activate virtual environment and run script
source testai-env/bin/activate
python3 scripts/seed_subtopics.py
