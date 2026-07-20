#!/bin/bash
# stop_backend_server.sh

echo "Stopping backend server..."

# Find and stop the python3 main.py process in fast_api_backend directory
PID=$(ps aux | grep "python3 main.py" | grep -v grep | grep -v "stop_backend_server" | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "No backend server process found."
else
    echo "Found backend server (PID: $PID). Stopping..."
    kill $PID

    # Wait a moment for graceful shutdown
    sleep 2

    # Force kill if still running
    if ps -p $PID > /dev/null; then
        echo "Process still running, force killing..."
        kill -9 $PID
    fi

    echo "Backend server stopped."
fi
