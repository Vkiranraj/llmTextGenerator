# LLM Text Generator - Docker Deployment

This guide will help you deploy the LLM Text Generator application using Docker containers.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 2GB of available RAM
- At least 5GB of available disk space

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd llmTextGenerator

# Create environment file
touch .env
# Edit .env with your settings (see Configuration section below)
```

### 2. Deploy

```bash
# Deploy the application
docker-compose up -d
```

### 3. Access the Application

- **Main App**: http://localhost
- **API Docs**: http://localhost/api/docs
- **Backend API**: http://localhost/api/

## Architecture

The application consists of four Docker services:

### Backend Service
- **Container**: `llm-text-generator-backend`
- **Port**: 8000 (internal)
- **Technology**: FastAPI + Python 3.9
- **Features**: URL crawling, LLM text generation, API endpoints

### Frontend Service
- **Container**: `llm-text-generator-frontend`
- **Port**: 3000 (internal)
- **Technology**: React + Node.js 18
- **Features**: User interface, job management, real-time updates

### Monitor Service
- **Container**: `llm-text-generator-monitor`
- **Technology**: Python + Cron
- **Features**: Automated URL monitoring, content change detection

### Nginx Service
- **Container**: `llm-text-generator-nginx`
- **Port**: 80 (external)
- **Technology**: Nginx Alpine
- **Features**: Reverse proxy, load balancing, SSL termination

## Service Management

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs nginx
docker-compose logs backend
docker-compose logs frontend
docker-compose logs monitor

# Follow logs in real-time
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f monitor
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

## Monitoring Features

### Automated Monitoring
- **Schedule**: Daily at 2:00 AM
- **Function**: Checks all URLs for content changes
- **Detection**: Uses content hashing for change detection
- **Action**: Automatically regenerates LLM text when changes detected

### Manual Monitoring
```bash
# Run monitoring manually
docker-compose exec monitor python scripts/monitor_urls.py
```

### View Monitoring Logs
```bash
# View monitoring logs
docker-compose logs monitor

# Follow monitoring logs in real-time
docker-compose logs -f monitor
```

## Data Persistence

### Database
- **Location**: `./backend/data/url_monitor.db`
- **Type**: SQLite database
- **Persistence**: Survives container restarts

### Generated Content
- **Storage**: Database (`llm_text_content` column)
- **Content**: Generated LLM text content
- **Access**: Via API endpoint `/jobs/{job_id}/download`
- **Persistence**: Survives container restarts

### Logs
- **Location**: `./backend/logs/`
- **Files**: `monitor.log`, application logs
- **Persistence**: Survives container restarts

## Development

### Build Individual Services
```bash
# Build nginx only
docker-compose build nginx

# Build backend only
docker-compose build backend

# Build frontend only
docker-compose build frontend

# Build monitor only
docker-compose build monitor
```

### Run in Development Mode
```bash
# Start with live reloading
docker-compose up --build

# Start in background
docker-compose up -d --build
```

### Access Container Shell
```bash
# Nginx container
docker-compose exec nginx sh

# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Monitor container
docker-compose exec monitor bash
```

## Configuration

### Environment Variables

The application is fully parameterized using environment variables. Create a `.env` file in the project root and configure the variables below:

```bash
# Create the environment file
touch .env
# Edit .env with your settings
```

#### Quick Setup (Minimum Configuration)

For a quick start, create a `.env` file with just these essential variables:

```bash
# Minimum required configuration
BASE_URL=http://localhost:8000
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-for-sensitive-data
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
OPENAI_API_KEY=your-openai-api-key
```

**Generate secure keys:**
```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY  
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

#### Complete .env File Example

For full configuration, create a `.env` file in the project root with the following content:

```bash
# Required Variables
BASE_URL=http://localhost:8000
DATABASE_URL=sqlite:///./data/url_monitor.db
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-encryption-key-for-sensitive-data

# Email Configuration (Required for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Optional Variables (with defaults)
MAX_PAGES=20
MAX_DEPTH=1
MAX_CONTENT_PARAGRAPHS=10
REQUESTS_TIMEOUT=10
PLAYWRIGHT_TIMEOUT=60000
GRACE_PERIOD_CRAWLS=2

# Frontend Variables
REACT_APP_API_BASE_URL=

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# Docker Variables
NGINX_PORT=80
DOMAIN_NAME=localhost
```

#### Required Variables
- `BASE_URL`: Application base URL (e.g., `http://localhost:8000` or `https://your-domain.com`)
- `DATABASE_URL`: Database connection string (default: `sqlite:///./data/url_monitor.db`)
- `SECRET_KEY`: Application secret key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `ENCRYPTION_KEY`: Encryption key for sensitive data (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

#### Email Configuration
- `SMTP_HOST`: SMTP server hostname (default: `smtp.gmail.com`)
- `SMTP_PORT`: SMTP server port (default: `587`)
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `FROM_EMAIL`: Sender email address

#### Optional Variables (with defaults)
- `MAX_PAGES`: Maximum pages to crawl (default: 20)
- `MAX_DEPTH`: Maximum crawl depth (default: 1)
- `MAX_CONTENT_PARAGRAPHS`: Max content paragraphs (default: 10)
- `REQUESTS_TIMEOUT`: Request timeout in seconds (default: 10)
- `PLAYWRIGHT_TIMEOUT`: Playwright timeout in ms (default: 60000)
- `GRACE_PERIOD_CRAWLS`: Crawls before deleting pages (default: 2)

#### Frontend Variables
- `REACT_APP_API_BASE_URL`: API base URL for frontend (leave empty for nginx proxy)

#### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI-enhanced content)
- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)
- `OPENAI_MAX_TOKENS`: Maximum tokens per request (default: 500)
- `OPENAI_TEMPERATURE`: Response creativity (default: 0.3)

#### Docker Variables
- `NGINX_PORT`: Nginx port (default: 80)
- `DOMAIN_NAME`: Domain name for nginx (default: localhost)

### Railway Deployment

For Railway deployment, set these variables in your Railway dashboard:

**Required:**
- `BASE_URL`: Your Railway app URL
- `SECRET_KEY`: Generate a secure random string
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`
- `OPENAI_API_KEY`: Your OpenAI API key for AI-enhanced content

**Optional:** All other variables will use defaults if not set.

### Port Configuration
- **Frontend**: 3000 (internal)
- **Backend**: 8000 (internal)
- **Nginx**: 80 (external, configurable via `NGINX_PORT`)

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
docker --version
docker-compose --version

# Check logs
docker-compose logs
```

#### Port Conflicts
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :8000

# Change ports in docker-compose.yml
```

#### Database Issues
```bash
# Reset database
docker-compose down
rm -rf backend/data
docker-compose up --build
```

#### Monitoring Issues
```bash
# Check monitor service
docker-compose logs monitor

# Run monitoring manually
docker-compose exec monitor python scripts/monitor_urls.py
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Test endpoints
curl http://localhost/
curl http://localhost/api/
curl http://localhost/api/docs
```

## Performance

### Resource Requirements
- **CPU**: 2 cores minimum, 4 cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB minimum, 10GB recommended

### Optimization
- Use SSD storage for better database performance
- Allocate sufficient RAM for Playwright browser instances
- Monitor disk space for generated files

## Security

### Network Security
- Services communicate through Docker internal network
- Only necessary ports exposed to host
- No external database dependencies

### Data Security
- SQLite database with file-based storage
- No sensitive data in environment variables
- Logs contain no sensitive information

## Logs

### Log Locations
- **Application Logs**: `docker-compose logs`
- **Monitoring Logs**: `./backend/logs/monitor.log`
- **Container Logs**: `docker logs <container-name>`

### Log Rotation
```bash
# Set up log rotation (optional)
sudo logrotate -f /etc/logrotate.conf
```

## Production Deployment

### Production Considerations
1. **Use a reverse proxy** (nginx) for SSL termination
2. **Set up log aggregation** (ELK stack)
3. **Configure monitoring** (Prometheus + Grafana)
4. **Use external database** (PostgreSQL) for production
5. **Set up backup strategy** for data persistence

### Example Production Setup
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

## Support

### Getting Help
1. Check the logs: `docker-compose logs`
2. Verify service status: `docker-compose ps`
3. Test endpoints: `curl http://localhost/`
4. Check Docker daemon: `docker info`

### Common Commands
```bash
# Full restart
docker-compose down && docker-compose up --build

# Clean restart (removes all data)
docker-compose down -v && docker-compose up --build

# Update application
git pull && docker-compose up --build
```

---

**You're all set!** Your LLM Text Generator is now running in Docker containers with automated monitoring.
