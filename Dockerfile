# Multi-stage build for single container deployment
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install --omit=dev

COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    cron \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Set working directory
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Make scripts executable
RUN chmod +x scripts/monitor_urls.py

# Expose port
EXPOSE 80

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "Starting services..."' >> /app/start.sh && \
    echo 'echo "DEMO_MODE: $DEMO_MODE"' >> /app/start.sh && \
    echo 'echo "MONITORING_INTERVAL_MINUTES: $MONITORING_INTERVAL_MINUTES"' >> /app/start.sh && \
    echo 'echo "HARDCODED DEMO MODE - 5 minute intervals"' >> /app/start.sh && \
    echo 'if true; then' >> /app/start.sh && \
    echo '    echo "Setting up demo mode cron (every 5 minutes)"' >> /app/start.sh && \
    echo '    echo "*/5 * * * * cd /app && python3 /app/scripts/monitor_urls.py >> /app/logs/monitor.log 2>&1" | crontab -' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '    echo "Setting up production mode cron (daily at 2 AM)"' >> /app/start.sh && \
    echo '    echo "0 2 * * * cd /app && python3 /app/scripts/monitor_urls.py >> /app/logs/monitor.log 2>&1" | crontab -' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'echo "Cron jobs set up:"' >> /app/start.sh && \
    echo 'crontab -l' >> /app/start.sh && \
    echo 'echo "Starting cron service..."' >> /app/start.sh && \
    echo 'service cron start' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo 'echo "Checking cron status..."' >> /app/start.sh && \
    echo 'ps aux | grep cron | grep -v grep && echo "Cron is running" || echo "Cron failed to start"' >> /app/start.sh && \
    echo 'echo "Starting FastAPI backend..."' >> /app/start.sh && \
    echo 'uvicorn app.main:app --host 0.0.0.0 --port 8000 &' >> /app/start.sh && \
    echo 'echo "Starting Nginx..."' >> /app/start.sh && \
    echo 'nginx -g "daemon off;"' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 80

# Start all services
CMD ["/app/start.sh"]
