#!/bin/bash
# Wrapper script to apply sessions migration with proper environment

# Load environment variables
set -a
source .env
set +a

# Activate virtual environment and run migration script
source testai-env/bin/activate
python3 scripts/apply_sessions_migration.py
