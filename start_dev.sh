#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
}
trap cleanup EXIT

echo "Starting Content Shield Development Environment..."

# Check for .env
if [ ! -f backend/.env ]; then
    echo "WARNING: backend/.env not found!"
    echo "Please create backend/.env and add your GEMINI_API_KEY before running."
    exit 1
fi

# Start Backend
echo "Starting Backend (Port 8000)..."
source backend/venv/bin/activate
# We run uvicorn in the background but let it print to stdout/stderr
set -a
[ -f backend/.env ] && source backend/.env
set +a
PYTHONPATH=$PYTHONPATH:$(pwd)/backend uvicorn backend.app.main:app --reload --port 8000 --log-level info &
BACKEND_PID=$!

# Give backend a moment to start
sleep 2

# Start Frontend
echo "Starting Frontend (Port 8080)..."
npm run dev -- --port 8080 &
FRONTEND_PID=$!

echo "Both servers started. Backend logs will appear below:"
echo "-----------------------------------------------------"

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
