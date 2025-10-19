# DigitalOcean App Platform Deployment Guide

This guide will walk you through deploying your LLM Text Generator application to DigitalOcean App Platform using Docker Compose.

## Prerequisites

*   A DigitalOcean account (sign up at https://cloud.digitalocean.com)
*   Your OpenAI API Key
*   GitHub repository with your code

## Deployment Steps

### 1. Create DigitalOcean Account
1. Go to https://cloud.digitalocean.com
2. Sign up for a DigitalOcean account
3. Add a payment method (required for App Platform)

### 2. Create New App
1. In DigitalOcean dashboard, click "Create" → "Apps"
2. Choose "GitHub" as source
3. Select your repository: `llmTextGenerator`
4. Choose "Docker Compose" as the deployment method

### 3. Configure App
DigitalOcean will automatically detect your `docker-compose.yml` file. You can configure:

**App Name**: `llm-text-generator` (or your preferred name)

**Environment Variables** (set in App Platform dashboard):
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql://user:password@host:port/database
```

**Optional Environment Variables**:
```
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3
MAX_PAGES=30
MAX_DEPTH=1
MAX_CONTENT_PARAGRAPHS=10
REQUESTS_TIMEOUT=10
PLAYWRIGHT_TIMEOUT=60000
CRAWL_DELAY=2
GRACE_PERIOD_CRAWLS=2
```

**Email Configuration (Optional)**:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### 4. Add PostgreSQL Database
1. In the App Platform dashboard, click "Create" → "Database"
2. Choose "PostgreSQL"
3. Select a name: `llm-text-generator-db`
4. Choose a plan (Basic $15/month or higher)
5. DigitalOcean will provide a `DATABASE_URL` automatically
6. Copy the `DATABASE_URL` and add it to your app environment variables

### 5. Deploy
1. Click "Create Resources"
2. DigitalOcean will automatically:
   - Build all Docker images from your `docker-compose.yml`
   - Start all services (backend, frontend, nginx, monitor)
   - Provide you with a public URL

### 6. Access Your Application
After deployment, DigitalOcean will provide you with a public URL like:
`https://llm-text-generator-xyz.ondigitalocean.app`

## Service Configuration

DigitalOcean will deploy all 4 services from your `docker-compose.yml`:

1. **Backend** - FastAPI application
2. **Frontend** - React application  
3. **Nginx** - Reverse proxy
4. **Monitor** - Background monitoring service

## Environment Variables Setup

### Generate Secret Keys:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (optional)
openssl rand -hex 32
```

### Set Variables in DigitalOcean Dashboard:
1. Go to your app in the dashboard
2. Click on "Settings" → "Environment Variables"
3. Add each variable with its value

## Database
DigitalOcean provides a managed PostgreSQL database. The application will use the `DATABASE_URL` environment variable.

## Monitoring
- Check logs: Available in App Platform dashboard
- Check status: Service health in dashboard
- View metrics: Built-in monitoring and alerting

## Troubleshooting
- Check application logs for errors
- Verify all environment variables are set
- Ensure OpenAI API key is valid and has credits
- Check database connection

## Production Considerations
- Set up proper email configuration for notifications
- Monitor OpenAI API usage and costs
- Set up monitoring and alerting
- Consider rate limiting for public access

## Pricing
- **App Platform**: $5/month for Basic plan
- **PostgreSQL Database**: $15/month for Basic plan
- **Total**: ~$20/month for production setup

## Advantages of DigitalOcean App Platform
- ✅ Native Docker Compose support
- ✅ Simple deployment process
- ✅ Automatic scaling
- ✅ Managed PostgreSQL database
- ✅ Built-in monitoring
- ✅ Easy environment variable management
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Production-ready infrastructure
