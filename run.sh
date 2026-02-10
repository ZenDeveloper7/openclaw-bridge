#!/bin/bash
# Run OpenClaw Admin Dashboard
set -e

cd "$(dirname "$0")"

# Install deps if needed
if [ ! -d "backend/.venv" ]; then
  echo "Setting up Python venv..."
  python -m venv backend/.venv
  backend/.venv/bin/pip install -r backend/requirements.txt
fi

# Serve frontend statically via FastAPI
# Copy frontend to dist for static serving
mkdir -p frontend/dist
cp frontend/index.html frontend/dist/
cp -r frontend/src frontend/dist/

echo "Starting OpenClaw Admin Dashboard on http://localhost:8787"
backend/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8787 --reload
