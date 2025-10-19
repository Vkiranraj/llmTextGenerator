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

# Copy startup script
COPY start.sh /app/start.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Make scripts executable
RUN chmod +x scripts/monitor_urls.py
RUN chmod +x /app/start.sh

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 80

# Start all services
CMD ["/app/start.sh"]
