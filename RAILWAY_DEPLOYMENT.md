# Railway Deployment Guide

## Prerequisites
1. Railway account (sign up at https://railway.app)
2. Railway CLI installed (`npm install -g @railway/cli`)
3. Git repository with your code

## Deployment Steps

### 1. Login to Railway
```bash
railway login
```

### 2. Initialize Railway Project
```bash
railway init
```

### 3. Set Environment Variables
You need to set these environment variables in Railway dashboard:

#### Required Variables:
- `SECRET_KEY` - Generate a secure secret key
- `ENCRYPTION_KEY` - Generate an encryption key (optional, uses SECRET_KEY if not set)
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Railway will provide PostgreSQL URL automatically

#### Optional Variables (with defaults):
- `OPENAI_MODEL` - Default: `gpt-4o-mini`
- `OPENAI_MAX_TOKENS` - Default: `500`
- `OPENAI_TEMPERATURE` - Default: `0.3`
- `MAX_PAGES` - Default: `30`
- `MAX_DEPTH` - Default: `1`
- `MAX_CONTENT_PARAGRAPHS` - Default: `10`
- `REQUESTS_TIMEOUT` - Default: `10`
- `PLAYWRIGHT_TIMEOUT` - Default: `60000`
- `CRAWL_DELAY` - Default: `2`
- `GRACE_PERIOD_CRAWLS` - Default: `2`

#### Email Configuration (Optional):
- `SMTP_HOST` - Default: `smtp.gmail.com`
- `SMTP_PORT` - Default: `587`
- `SMTP_USER` - Your email
- `SMTP_PASSWORD` - Your email password
- `FROM_EMAIL` - Your from email

### 4. Deploy
```bash
railway up
```

### 5. Get Your Domain
```bash
railway domain
```

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
2. Click on "Variables" tab
3. Add each variable with its value

## Database
Railway automatically provides a PostgreSQL database. The application will use the `DATABASE_URL` environment variable.

## Monitoring
- Check logs: `railway logs`
- Check status: `railway status`
- View metrics in Railway dashboard

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
