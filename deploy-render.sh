#!/bin/bash

# Render Deployment Script
echo "Starting Render Deployment..."

# Check if user is logged in to Render CLI (optional)
if command -v render &> /dev/null; then
    echo "Render CLI found. Checking authentication..."
    render auth || echo "Please login to Render CLI: render auth"
else
    echo "Render CLI not found. You can install it with: npm install -g @render/cli"
    echo "Or use the web dashboard at https://render.com"
fi

echo ""
echo "Deployment Steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login with GitHub"
echo "3. Click 'New +' -> 'Web Service'"
echo "4. Connect your GitHub repository: $(git remote get-url origin)"
echo "5. Choose 'Docker Compose' as deployment method"
echo "6. Set environment variables:"
echo ""
echo "Required:"
echo "- SECRET_KEY (generate with: openssl rand -hex 32)"
echo "- OPENAI_API_KEY (your OpenAI API key)"
echo ""
echo "Optional (with defaults):"
echo "- OPENAI_MODEL (default: gpt-4o-mini)"
echo "- OPENAI_MAX_TOKENS (default: 500)"
echo "- OPENAI_TEMPERATURE (default: 0.3)"
echo "- MAX_PAGES (default: 30)"
echo "- MAX_DEPTH (default: 1)"
echo ""
echo "7. Add PostgreSQL database:"
echo "   - Click 'New +' -> 'PostgreSQL'"
echo "   - Copy DATABASE_URL to web service environment"
echo ""
echo "8. Click 'Create Web Service'"
echo ""
echo "Your application will be available at: https://your-app-name.onrender.com"
echo ""
echo "For detailed instructions, see RENDER_DEPLOYMENT.md"
