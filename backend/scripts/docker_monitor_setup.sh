#!/bin/bash

# Docker Monitoring Setup Script
echo "🐳 Setting up monitoring for Docker environment..."

# Create logs directory
mkdir -p /app/logs

# Set up cron job for monitoring
echo "0 2 * * * cd /app && python scripts/monitor_urls.py >> /app/logs/monitor.log 2>&1" | crontab -

echo "✅ Docker monitoring setup complete!"
echo "📅 Cron job scheduled: Daily at 2:00 AM"
echo "📝 Logs will be saved to: /app/logs/monitor.log"
