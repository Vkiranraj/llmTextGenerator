#!/bin/bash

echo "🗑️  Resetting database for fresh start..."

# Remove existing database
rm -f backend/url_monitor.db

# Remove any existing llm files
rm -f llms_*.txt

echo "✅ Database reset complete!"
echo "📝 You can now start fresh with the new monitoring system."
