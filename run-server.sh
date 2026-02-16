#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8000}"

echo "========================================"
echo "  Build & Run: YT Transcribe"
echo "========================================"
echo

# --- Build frontend ---
echo "--- Building frontend ---"
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install --silent
fi

npx vite build
echo "✓ Frontend built"
echo

# --- Copy to backend/static ---
echo "--- Deploying to backend/static ---"
rm -rf "$ROOT_DIR/backend/static"
cp -r "$ROOT_DIR/frontend/dist" "$ROOT_DIR/backend/static"
echo "✓ Copied to backend/static"
echo

# --- Start backend ---
echo "--- Starting backend server ---"
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

URL="http://localhost:$PORT"
echo "Server will be available at: $URL"
echo

# Try to open browser (works on WSL, macOS, and Linux with xdg-open)
open_browser() {
    if command -v wslview &>/dev/null; then
        wslview "$1" &
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$1" &
    elif command -v open &>/dev/null; then
        open "$1" &
    elif command -v explorer.exe &>/dev/null; then
        explorer.exe "$1" &
    else
        echo "(Could not auto-open browser. Open $1 manually.)"
        return
    fi
    echo "✓ Opened browser"
}

if [ "${NO_BROWSER:-}" != "1" ]; then
    # Open browser after a short delay to let the server start
    (sleep 2 && open_browser "$URL") &
fi

echo "Press Ctrl+C to stop."
echo
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
