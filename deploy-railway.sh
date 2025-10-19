#!/bin/bash

# Railway Deployment Script
echo "Starting Railway Deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "Checking Railway authentication..."
railway whoami || railway login

# Initialize Railway project (if not already initialized)
echo "Initializing Railway project..."
railway init

# Set up environment variables
echo "Setting up environment variables..."
echo "Please set the following environment variables in Railway dashboard:"
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
echo "Email Configuration (optional):"
echo "- SMTP_HOST (default: smtp.gmail.com)"
echo "- SMTP_PORT (default: 587)"
echo "- SMTP_USER (your email)"
echo "- SMTP_PASSWORD (your email password)"
echo "- FROM_EMAIL (your from email)"
echo ""

# Deploy to Railway
echo "Deploying to Railway..."
railway up

# Get the domain
echo "Getting your Railway domain..."
railway domain

echo "Deployment complete!"
echo "Check your Railway dashboard for logs and monitoring."
