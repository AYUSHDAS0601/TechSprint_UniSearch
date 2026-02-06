#!/bin/bash

# setup_arch.sh - Setup script for Digital Archaeology on Arch Linux
# Usage: ./setup_arch.sh

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  DIGITAL ARCHAEOLOGY - ARCH LINUX SETUP"
echo "═══════════════════════════════════════════════════════════════"

# Check for sudo
if [[ $EUID -eq 0 ]]; then
   echo "Error: This script must NOT be run as root directly, but requires sudo for pacman."
   echo "Please run as normal user: ./setup_arch.sh"
   exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "[*] Project Directory: $PROJECT_DIR"

# 1. Install System Dependencies
echo ""
echo "[1/4] Installing System Dependencies (requires sudo)..."
echo "      Packages: python, python-pip, tesseract, tesseract-data-eng, poppler"
sudo pacman -Sy --needed --noconfirm python python-pip tesseract tesseract-data-eng poppler base-devel

# 2. Setup Virtual Environment
echo ""
echo "[2/4] Setting up Python Virtual Environment..."
if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
    echo "      Virtual environment created at $VENV_DIR"
else
    echo "      Virtual environment already exists."
fi

# Activate venv for installation
source "$VENV_DIR/bin/activate"

# 3. Install Python Dependencies
echo ""
echo "[3/4] Installing Python Packages from requirements.txt..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/requirements.txt"
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# 4. Download Language Models (Pre-cache)
echo ""
echo "[4/4] Pre-downloading sentence-transformers model..."
python -c "from sentence_transformers import SentenceTransformer; print('Downloading model...'); SentenceTransformer('all-MiniLM-L6-v2')"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo "To run the application:"
echo "  ./run.sh"
echo ""
