#!/bin/bash

# Docker Logs Script for LLM Text Generator
echo "📝 Viewing LLM Text Generator logs..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ No services are running. Start services first:"
    echo "   ./docker-deploy.sh"
    exit 1
fi

echo "🔍 Available services:"
echo "   backend, frontend, monitor"
echo ""

# Show logs for all services or specific service
if [ $# -eq 0 ]; then
    echo "📊 Showing logs for all services..."
    docker-compose logs -f
else
    SERVICE=$1
    echo "📊 Showing logs for $SERVICE service..."
    docker-compose logs -f $SERVICE
fi
