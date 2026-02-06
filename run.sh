#!/bin/bash

# run.sh - Quick launch script for Digital Archaeology
# Usage: ./run.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run ./setup_arch.sh first."
    exit 1
fi

echo "Starting Digital Archaeology..."
source "$VENV_DIR/bin/activate"

# Verify Tesseract installation
if ! command -v tesseract &> /dev/null; then
    echo "Warning: tesseract is not in your PATH. Ensure 'tesseract' is installed via pacman."
fi

streamlit run "$PROJECT_DIR/app.py" --server.port 8501
