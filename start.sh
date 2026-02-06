#!/bin/bash

# start.sh - Unified startup script for Digital Archaeology MERN Stack
# Usage: ./start.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔═══════════════════════════════════════════╗"
echo "║  🏛️  DIGITAL ARCHAEOLOGY v3.0 MERN       ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed."
    echo "Please install npm first: sudo pacman -S npm"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "Please install Node.js first: sudo pacman -S nodejs"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"
echo "✅ npm $(npm --version) detected"
echo ""

# Install backend dependencies if needed
if [ ! -d "$PROJECT_DIR/backend/node_modules" ]; then
    echo "📦 Installing backend dependencies..."
    cd "$PROJECT_DIR/backend"
    npm install
    echo "✅ Backend dependencies installed"
    echo ""
fi

# Install frontend dependencies if needed
if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd "$PROJECT_DIR/frontend"
    npm install
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Start backend server in background
echo "🚀 Starting backend server on port 5000..."
cd "$PROJECT_DIR/backend"
npm start &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait a moment for backend to initialize
sleep 2

# Start frontend dev server
echo "🚀 Starting frontend dev server on port 3000..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "╔═══════════════════════════════════════════╗"
echo "║  🎉 DIGITAL ARCHAEOLOGY IS RUNNING!      ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
