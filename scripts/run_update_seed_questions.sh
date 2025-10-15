#!/bin/bash
# Update seed questions with proper subtopics and load into database

# Load environment variables
set -a
source .env
set +a

# Activate virtual environment and run update script
source testai-env/bin/activate
python3 scripts/update_seed_questions.py
