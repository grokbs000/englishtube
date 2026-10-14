#!/bin/bash
cd "$(dirname "$0")"
PORT=8885
if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8885 is already in use. Stop the existing server first."
  read -r -p "Press Enter to close..."
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "Setting up isolated Python environment..."
  python3 -m venv .venv || { echo "Please install Python 3 first."; read -r; exit 1; }
fi
if ! .venv/bin/python -c 'import yt_dlp' >/dev/null 2>&1; then
  echo "Installing YouTube caption support..."
  .venv/bin/python -m pip install -r requirements.txt || { echo "Install failed. Check internet access and try again."; read -r; exit 1; }
fi
echo "ENGLISHTUBE is running at http://localhost:$PORT"
open "http://localhost:$PORT" 2>/dev/null || true
.venv/bin/python server.py
