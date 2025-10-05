#!/bin/bash

# LLM Text Generator - Demo Startup Script

echo "🚀 Starting LLM Text Generator Demo..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure:"
    echo "   ├── backend/"
    echo "   ├── frontend/"
    echo "   └── start_demo.sh"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend might already be running."
fi

echo ""
echo "📋 Demo Setup Instructions:"
echo ""
echo "1. Backend (FastAPI):"
echo "   cd backend"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Frontend (Static files):"
echo "   cd frontend"
echo "   python -m http.server 3000"
echo ""
echo "3. Access the application:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Monitoring Features:"
echo "   ✅ Automatic daily monitoring (2 AM)"
echo "   ✅ Content change detection"
echo "   ✅ Automatic LLM text regeneration"
echo "   📝 Check logs: tail -f backend/monitor.log"
echo ""
echo "💡 Tips:"
echo "   - Keep both terminals open"
echo "   - Backend must be running before frontend"
echo "   - Monitoring runs automatically in background"
echo ""
echo "🎯 Ready to start your demo!"
