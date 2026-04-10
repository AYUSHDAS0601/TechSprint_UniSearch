#!/bin/bash
# run.sh — Digital Archaeology launch script
# Usage:  ./run.sh            (starts modern FastAPI + Vite stack)
#         ./run.sh legacy     (starts legacy Streamlit app)

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
NODE_FIX_DIR="$PROJECT_DIR/node_fix"
FRONTEND_DIR="$PROJECT_DIR/frontend"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌  Virtual environment not found. Run ./setup_arch.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

if ! command -v tesseract &>/dev/null; then
    echo "⚠   Warning: tesseract not in PATH. OCR features may not work."
fi

# ─── legacy mode ─────────────────────────────────────────────────────────────
if [ "${1:-}" = "legacy" ]; then
    echo "🚀  Starting Digital Archaeology — Legacy Streamlit mode…"
    export HF_HUB_OFFLINE=1
    streamlit run "$PROJECT_DIR/app.py" --server.port 8501
    exit 0
fi

# ─── modern mode ─────────────────────────────────────────────────────────────
echo "🚀  Starting Digital Archaeology — Modern Stack (FastAPI + React)"
echo ""

# Kill any stale processes
pkill -f "backend/main.py" 2>/dev/null || true
sleep 0.5

# Start FastAPI backend
echo "📡  Backend  →  http://localhost:8000  (FastAPI)"
python "$PROJECT_DIR/backend/main.py" &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Vite frontend
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦  Installing frontend dependencies…"
    cd "$FRONTEND_DIR"
    LD_LIBRARY_PATH="$NODE_FIX_DIR:${LD_LIBRARY_PATH:-}" npm install
fi

echo "🎨  Frontend →  http://localhost:5173  (Vite + React)"
echo ""
echo "  Press Ctrl+C to stop both services."
echo ""

cd "$FRONTEND_DIR"
export LD_LIBRARY_PATH="$NODE_FIX_DIR:${LD_LIBRARY_PATH:-}"
npm run dev --host &
FRONTEND_PID=$!

# Cleanup on exit
trap 'echo ""; echo "Stopping..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT TERM

wait
