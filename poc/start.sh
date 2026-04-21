#!/bin/bash
# KriyaDocs AI Onboarding Platform — POC Startup Script
#
# Prerequisites:
#   1. (Optional) Set your OpenAI API key in poc/backend/.env:
#      OPENAI_API_KEY=sk-your-key-here
#      Not needed if cache/ directory is pre-populated.
#   2. Python 3.9+ and Node.js 18+ installed
#
# Usage: ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  KriyaDocs AI Onboarding Platform — POC"
echo "============================================"
echo ""

# Check for .env
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
  echo "NOTE: No .env file found."
  echo "The demo will use cached AI results if available."
  echo "To run with live AI, create poc/backend/.env with:"
  echo "  OPENAI_API_KEY=sk-your-key-here"
  echo ""
  echo "Get a key at: https://platform.openai.com/"
  echo ""
  echo "Continuing with cached/local mode..."
fi

# Start backend
echo "[1/2] Starting backend (FastAPI on port 8001)..."
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Starting frontend (Vite on port 3000)..."
cd "$SCRIPT_DIR/frontend"
npx vite --port 3000 &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "  Ready!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8001"
echo "  API Docs: http://localhost:8001/docs"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop both servers."

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
