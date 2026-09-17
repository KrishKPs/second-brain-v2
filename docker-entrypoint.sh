#!/bin/sh
set -e

WATCH_FOLDER=${WATCH_FOLDER:-/screenshots}

# Start the API server in the background
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Wait until the server is accepting requests
echo "[startup] Waiting for server..."
until curl -sf http://localhost:8000/health >/dev/null 2>&1; do
  sleep 1
done
echo "[startup] Server ready."

# Index the screenshots folder on every container start so nothing is missed
python -c "
from src.brain import SecondBrain
r = SecondBrain().index('$WATCH_FOLDER')
print(f'[startup] Indexed {r[\"indexed\"]} new, skipped {r[\"skipped\"]}, failed {r[\"failed\"]}')
"

# Hand off to the watcher — container lives as long as the watcher does
exec python watcher.py "$WATCH_FOLDER"
