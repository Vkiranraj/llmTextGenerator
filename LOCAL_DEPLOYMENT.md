# Local Deployment Guide

This guide will help you deploy the LLM Text Generator application locally using Docker.

## Prerequisites

- Docker installed
- Git (to clone the repository)
- OpenAI API key (optional, for AI-enhanced features)

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd llmTextGenerator
```

### 2. Create Environment File
```bash
touch .env
```

### 3. Configure Environment Variables
Edit the `.env` file with your settings:

```bash
# Application Configuration
BASE_URL=http://localhost:8000

# Database Configuration
DATABASE_URL=sqlite:///./data/url_monitor.db

# Security Configuration
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# Crawling Configuration
MAX_PAGES=30
MAX_DEPTH=1
MAX_CONTENT_PARAGRAPHS=10
REQUESTS_TIMEOUT=10
PLAYWRIGHT_TIMEOUT=60000
CRAWL_DELAY=2
GRACE_PERIOD_CRAWLS=2

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Docker Configuration
NGINX_PORT=80
DOMAIN_NAME=localhost
```

### 4. Generate Secret Keys
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY (optional)
openssl rand -hex 32
```

### 5. Start the Application
```bash
# Build and run the Docker container
docker build -t llm-text-generator .
docker run -d -p 80:80 --env-file .env --name llm-text-generator llm-text-generator
```

### 6. Access the Application
Open your browser and go to: `http://localhost`

## Detailed Setup

### Environment Variables Explained

#### Required Variables:
- `SECRET_KEY` - Used for session security and encryption
- `BASE_URL` - The base URL of your application (for local development: http://localhost:8000)

#### Optional Variables:
- `OPENAI_API_KEY` - Your OpenAI API key for AI-enhanced categorization and summaries
- `ENCRYPTION_KEY` - Additional encryption key (uses SECRET_KEY if not set)
- `MAX_PAGES` - Maximum number of pages to crawl (default: 30)
- `MAX_DEPTH` - Maximum crawl depth (default: 1)
- `MAX_CONTENT_PARAGRAPHS` - Maximum paragraphs to extract per page (default: 10)

#### Email Configuration (Optional):
- `SMTP_HOST` - SMTP server for email notifications
- `SMTP_PORT` - SMTP port (usually 587 for TLS)
- `SMTP_USER` - Your email username
- `SMTP_PASSWORD` - Your email password or app password
- `FROM_EMAIL` - The "from" email address for notifications

### Docker Services

The application runs in a single Docker container with 4 services:

1. **Backend** - FastAPI application with Python (port 8000)
2. **Frontend** - React static files served by Nginx
3. **Monitor** - Background monitoring service
4. **Nginx** - Reverse proxy and static file server (port 80)

### Database

The application uses SQLite by default for local development. The database file is stored in `./backend/data/url_monitor.db`.

### File Structure

```
llmTextGenerator/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   ├── data/               # Database files
│   └── logs/               # Log files
├── frontend/               # React frontend
├── docker-compose.yml      # Docker services configuration
├── nginx.conf              # Nginx configuration
└── .env                    # Environment variables
```

## Usage

### 1. Add URLs to Monitor
- Open the web interface at `http://localhost`
- Enter the URL you want to monitor
- Click "Start Monitoring"

### 2. View Results
- The application will crawl the website
- Generate AI-enhanced summaries (if OpenAI is configured)
- Create organized LLM text files
- Display results in the web interface

### 3. Download Generated Content
- View the generated LLM text content
- Copy or download the formatted content
- Use for AI model training or analysis

### Logs and Debugging

#### View Application Logs
```bash
# View container logs
docker logs llm-text-generator

# Follow logs in real-time
docker logs -f llm-text-generator
```

#### Check Container Status
```bash
docker ps
```

#### Restart Container
```bash
# Stop and restart the container
docker stop llm-text-generator
docker start llm-text-generator
```

## Development

### Making Changes

1. **Backend Changes**: Edit files in `backend/app/`
2. **Frontend Changes**: Edit files in `frontend/src/`
3. **Configuration Changes**: Edit `Dockerfile` or `nginx.conf`

### Rebuilding After Changes
```bash
# Rebuild and restart
docker build -t llm-text-generator .
docker stop llm-text-generator
docker rm llm-text-generator
docker run -d -p 80:80 --env-file .env --name llm-text-generator llm-text-generator
```

### Database Management
```bash
# Access database directly
docker exec -it llm-text-generator python -c "
from app.database import get_db
from app.models import URLJob
db = next(get_db())
jobs = db.query(URLJob).all()
print(f'Total jobs: {len(jobs)}')
"
```

#

