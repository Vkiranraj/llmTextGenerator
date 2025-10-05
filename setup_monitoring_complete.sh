#!/bin/bash

echo "🚀 Setting up Complete URL Monitoring System..."

# 1. Reset database
echo "🗑️  Resetting database..."
./reset_database.sh

# 2. Set up monitoring script
echo "🔧 Setting up monitoring script..."
cd backend
chmod +x scripts/monitor_urls.py

# 3. Set up cron job
echo "⏰ Setting up cron job..."
chmod +x scripts/setup_monitoring.sh
./scripts/setup_monitoring.sh

echo "✅ Complete monitoring setup finished!"
echo ""
echo "📋 What's been set up:"
echo "   ✅ Database reset (fresh start)"
echo "   ✅ Monitoring script created"
echo "   ✅ Cron job scheduled (daily at 2 AM)"
echo ""
echo "🔍 To test monitoring manually:"
echo "   cd backend && python scripts/monitor_urls.py"
echo ""
echo "📊 To check cron jobs:"
echo "   crontab -l"
echo ""
echo "📝 To view logs:"
echo "   tail -f backend/monitor.log"
