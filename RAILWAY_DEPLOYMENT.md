# Railway Deployment Guide

This guide will walk you through deploying your LLM Text Generator application to Railway.

## Prerequisites

*   A Railway account (sign up at https://railway.app)
*   Your OpenAI API Key
*   GitHub repository with your code

## Deployment Steps

### 1. Create Railway Account
1. Go to https://railway.app
2. Sign up with your GitHub account
3. Connect your GitHub repository

### 2. Create New Project
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `llmTextGenerator`
4. Railway will automatically detect your `Dockerfile`

### 3. Configure Service
Railway will automatically detect your `Dockerfile`. You can configure:

**Service Name**: `llm-text-generator` (or your preferred name)

**Port**: `80` (Railway will ask for this)

**Environment Variables** (set in Railway dashboard):
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
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
1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically provide a `DATABASE_URL` environment variable
3. No additional configuration needed

### 5. Deploy
1. Click "Deploy"
2. Railway will automatically:
   - Build your Dockerfile
   - Start all services in one container (backend, frontend, nginx, monitor)
   - Provide you with a public URL

### 6. Access Your Application
After deployment, Railway will provide you with a public URL like:
`https://your-app-name.railway.app`

## Environment Variables Setup

### Generate Secret Keys:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (optional)
openssl rand -hex 32
```

### Set Variables in Railway Dashboard:
1. Go to your project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add each variable with its value

## Database
Railway automatically provides a PostgreSQL database. The application will use the `DATABASE_URL` environment variable.

## Monitoring
- Check logs: Available in Railway dashboard
- Check status: Service health in dashboard
- View metrics: Built-in monitoring

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
- **Free Tier**: 500 hours/month
- **Pro Plan**: $5/month for always-on service
- **Database**: Included in Pro plan

## Advantages of Railway
- ✅ Simple deployment process
- ✅ Automatic database provisioning
- ✅ Built-in monitoring
- ✅ Easy environment variable management
- ✅ Automatic HTTPS
- ✅ Global CDN
