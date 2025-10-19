# Render Deployment Guide for LLM Text Generator

This guide will walk you through deploying your LLM Text Generator application to Render using Docker Compose.

## Prerequisites

*   A Render account (sign up at https://render.com)
*   Your OpenAI API Key
*   GitHub repository with your code

## Deployment Steps

### 1. Create Render Account
1. Go to https://render.com
2. Sign up with your GitHub account
3. Connect your GitHub repository

### 2. Create New Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository: `llmTextGenerator`
4. Choose "Docker Compose" as the deployment method

### 3. Configure Service
Render will automatically detect your `docker-compose.yml` file. You can configure:

**Service Name**: `llm-text-generator` (or your preferred name)

**Environment Variables** (set in Render dashboard):
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
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Choose a name: `llm-text-generator-db`
4. Render will provide a `DATABASE_URL` automatically
5. Copy the `DATABASE_URL` and add it to your web service environment variables

### 5. Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Build all Docker images
   - Start all services (backend, frontend, nginx, monitor)
   - Provide you with a public URL

### 6. Access Your Application
After deployment, Render will provide you with a public URL like:
`https://llm-text-generator.onrender.com`

## Service Configuration

Render will deploy all 4 services from your `docker-compose.yml`:

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

### Set Variables in Render Dashboard:
1. Go to your web service
2. Click on "Environment" tab
3. Add each variable with its value

## Database
Render automatically provides a PostgreSQL database. The application will use the `DATABASE_URL` environment variable.

## Monitoring
- Check logs: Available in Render dashboard
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
- **Free Tier**: 750 hours/month (enough for testing)
- **Starter Plan**: $7/month for always-on service
- **Database**: Free tier available

## Advantages of Render
- ✅ Native Docker Compose support
- ✅ Simple deployment process
- ✅ Automatic scaling
- ✅ Built-in PostgreSQL
- ✅ Free tier available
- ✅ Easy environment variable management
- ✅ Automatic HTTPS
- ✅ Global CDN
