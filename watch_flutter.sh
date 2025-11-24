#!/bin/bash
PROJECT_DIR="/app/project"
WEB_PORT=8080

# Function to start Flutter
start_flutter() {
    echo "[watcher] Starting Flutter web-server..."
    flutter run -d web-server --web-port=$WEB_PORT --web-hostname=0.0.0.0 &
    FLUTTER_PID=$!
    echo "[watcher] Flutter PID: $FLUTTER_PID"
}

# Start Flutter initially
start_flutter

# Watch for changes
inotifywait -m -r -e modify,create,delete "$PROJECT_DIR" |
while read -r path action file; do
    echo "[watcher] Change detected: $path$file ($action)"
    
    # Kill existing Flutter process
    if ps -p $FLUTTER_PID > /dev/null; then
        echo "[watcher] Killing Flutter process..."
        kill $FLUTTER_PID
        wait $FLUTTER_PID 2>/dev/null
        echo "[watcher] Flutter stopped."
    fi

    # Restart Flutter
    start_flutter
done
