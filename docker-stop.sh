#!/bin/bash

# Docker Stop Script for LLM Text Generator
echo "🛑 Stopping LLM Text Generator services..."

# Stop all services
docker-compose down

echo "✅ All services stopped!"
echo ""
echo "🔄 To restart services:"
echo "   ./docker-deploy.sh"
echo ""
echo "🗑️  To remove all data (WARNING: This will delete all data):"
echo "   docker-compose down -v"
echo "   sudo rm -rf backend/data backend/logs"
