# Multi-stage build for Railway deployment
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

# Start all services
CMD sh -c " \
    # Start FastAPI backend in the background \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
    # Start Playwright monitor in the background \
    python scripts/monitor_urls.py & \
    # Start Nginx in the foreground \
    nginx -g 'daemon off;' \
"
