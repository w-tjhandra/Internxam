#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_PORT="${PORT:-}"
FRONTEND_PID=""
BACKEND_PID=""

if [[ -z "$FRONTEND_PORT" && -f "$FRONTEND_DIR/.env" ]]; then
    FRONTEND_PORT="$(sed -n 's/^PORT=\([0-9][0-9]*\)$/\1/p' "$FRONTEND_DIR/.env" | head -n 1)"
fi
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM

    for pid in "$FRONTEND_PID" "$BACKEND_PID"; do
        if [[ -n "$pid" ]]; then
            kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    for pid in "$FRONTEND_PID" "$BACKEND_PID"; do
        if [[ -n "$pid" ]]; then
            wait "$pid" 2>/dev/null || true
        fi
    done

    exit "$exit_code"
}

if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is required to run the frontend." >&2
    exit 1
fi

if ! command -v uvicorn >/dev/null 2>&1; then
    echo "Error: uvicorn is required. Install backend/requirements.txt first." >&2
    exit 1
fi

if ! command -v setsid >/dev/null 2>&1; then
    echo "Error: setsid is required to stop both development servers cleanly." >&2
    exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    echo "Error: frontend dependencies are missing. Run a package install in frontend/ first." >&2
    exit 1
fi

if [[ ! -f "$BACKEND_DIR/.env" ]]; then
    echo "Warning: backend/.env was not found; configure DB_DSN and JWT_SECRET before use." >&2
fi

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

setsid bash -c 'cd "$1" && exec env REACT_APP_BACKEND_URL= npm start' _ "$FRONTEND_DIR" &
FRONTEND_PID=$!

setsid bash -c 'cd "$1" && exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000' _ "$BACKEND_DIR" &
BACKEND_PID=$!

echo "Frontend: https://localhost:$FRONTEND_PORT"
echo "Backend:  http://127.0.0.1:8000"
echo "Press Ctrl+C to stop both servers."

if wait -n "$FRONTEND_PID" "$BACKEND_PID"; then
    exit_code=0
else
    exit_code=$?
fi

if (( exit_code != 0 )); then
    echo "A development server exited with status $exit_code." >&2
fi

exit "$exit_code"
