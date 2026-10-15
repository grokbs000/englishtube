#!/bin/bash
PORT=8885
PID=$(lsof -nP -iTCP:$PORT -sTCP:LISTEN | awk 'NR>1 {print $2}' | head -1)
if [ -n "$PID" ]; then
  kill "$PID" && echo "✓ ENGLISHTUBE server stopped (PID $PID)."
else
  echo "No ENGLISHTUBE server running on port $PORT."
fi
read -r -p "Press Enter to close..."
