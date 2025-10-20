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

### 3. Add Persistent PostgreSQL Database
**IMPORTANT**: To prevent database resets on deployment, you need to add a persistent PostgreSQL database:

1. **In your Railway project dashboard, click "New Service"**
2. **Select "Database" → "PostgreSQL"**
3. **This creates a persistent database that won't reset on deployments**
4. **Railway will automatically provide the `DATABASE_URL` environment variable**

### 4. Configure Service
Railway will automatically detect your `Dockerfile`. You can configure:

**Service Name**: `llm-text-generator` (or your preferred name)

**Port**: `80` based on our docker file setting to obtain the domain link

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
GRACE_PERIOD_CRAWLS=2
MONITORING_INTERVAL_MINUTES=1440
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

## Database Persistence

### Why Database Resets Happen
By default, Railway uses ephemeral storage that gets reset on each deployment. This is why your PostgreSQL database data disappears.

### Solution: Persistent PostgreSQL Database
1. **Add PostgreSQL Service**: In your Railway project, click "New Service" → "Database" → "PostgreSQL"
2. **Add Configuration**: Set the railway `DATABASE_URL` environment variable
3. **Persistent Storage**: This database will persist across deployments and won't reset

### Verify Database Persistence
After adding the PostgreSQL service:
1. **Check Environment Variables**: The `DATABASE_URL` should be automatically set
2. **Test Deployment**: Deploy your app and add some data
3. **Redeploy**: Trigger a new deployment
4. **Verify Data**: Your data should still be there after redeployment

### Database Connection
Your application will automatically use the persistent PostgreSQL database instead of SQLite when the `DATABASE_URL` environment variable is set.

## Database
Railway automatically provides a PostgreSQL database. The application will use the `DATABASE_URL` environment variable.