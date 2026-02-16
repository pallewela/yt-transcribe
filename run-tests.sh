#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

echo "========================================"
echo "  Running all tests"
echo "========================================"
echo

# --- Backend tests ---
echo "--- Backend tests (pytest) ---"
echo
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

if python -m pytest -v; then
    echo
    echo "✓ Backend tests PASSED"
    PASS=$((PASS + 1))
else
    echo
    echo "✗ Backend tests FAILED"
    FAIL=$((FAIL + 1))
fi

deactivate 2>/dev/null || true
echo

# --- Frontend tests ---
echo "--- Frontend tests (vitest) ---"
echo
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install --silent
fi

if npx vitest run; then
    echo
    echo "✓ Frontend tests PASSED"
    PASS=$((PASS + 1))
else
    echo
    echo "✗ Frontend tests FAILED"
    FAIL=$((FAIL + 1))
fi

echo
echo "========================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "========================================"

[ "$FAIL" -eq 0 ] || exit 1
