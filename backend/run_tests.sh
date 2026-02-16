#!/usr/bin/env bash
# Run backend tests with code coverage.
# Usage: from project root, ./backend/run_tests.sh
#        or from backend: ./run_tests.sh
# Uses backend/venv if present, otherwise current python.

set -e
cd "$(dirname "$0")"
if [ -d "venv" ]; then
  exec ./venv/bin/python -m pytest --cov=app --cov-report=term-missing "$@"
else
  exec python -m pytest --cov=app --cov-report=term-missing "$@"
fi
