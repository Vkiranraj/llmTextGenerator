#!/bin/bash

# Start script for Railway deployment

echo "Starting LLM Text Generator services..."

# Start FastAPI backend in the background
echo "Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done

# Start Playwright monitor in the background
echo "Starting Playwright monitor..."
python scripts/monitor_urls.py &
MONITOR_PID=$!

# Wait a moment for services to stabilize
sleep 5

# Start Nginx in the foreground
echo "Starting Nginx..."
nginx -g 'daemon off;'
