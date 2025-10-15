#!/bin/bash
# Reset question bank for subtopic implementation

# Load environment variables
set -a
source .env
set +a

# Activate virtual environment and run reset script
source testai-env/bin/activate
python3 scripts/reset_question_bank.py
