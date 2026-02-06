#!/bin/bash

# run_phase2.sh - Launch Digital Archaeology Phase 2
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Run ./setup_arch.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Update dependencies if needed
echo "Checking Phase 2 dependencies..."
pip install -r requirements.txt | grep -v "Requirement already satisfied"

# Start Background Monitor in background
echo "Starting File Monitor Daemon..."
python monitor_daemon.py &
MONITOR_PID=$!

echo "Monitor PID: $MONITOR_PID"

# Start UI
echo "Starting Streamlit UI..."
streamlit run app.py --server.port 8501

# Cleanup on exit
kill $MONITOR_PID
