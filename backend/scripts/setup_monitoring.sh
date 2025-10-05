#!/bin/bash

# URL Monitoring Setup Script
echo "🔧 Setting up URL monitoring..."

# Get the absolute path to the project
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITOR_SCRIPT="$PROJECT_DIR/scripts/monitor_urls.py"
PYTHON_PATH="$PROJECT_DIR/../llmTextGenerator/bin/python"

# Make the monitor script executable
chmod +x "$MONITOR_SCRIPT"

# Create a cron job that runs every 24 hours at 2 AM
CRON_JOB="0 2 * * * cd $PROJECT_DIR && $PYTHON_PATH $MONITOR_SCRIPT >> $PROJECT_DIR/monitor.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Monitoring setup complete!"
echo "📅 Cron job added: Runs daily at 2:00 AM"
echo "📝 Logs will be saved to: $PROJECT_DIR/monitor.log"
echo ""
echo "🔍 To check cron jobs: crontab -l"
echo "🗑️  To remove monitoring: crontab -e (then delete the line)"
