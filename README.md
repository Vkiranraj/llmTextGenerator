# LLM Text Generator

A web application that crawls websites and generates AI-enhanced, organized text content optimized for Large Language Models (LLMs).
Here is a live deployed version: https://llmtextgenerator-production.up.railway.app/
## Features

- **Web Crawling**: Automatically crawls websites up to configurable depth
- **AI Enhancement**: Uses OpenAI for intelligent categorization and summaries
- **LLM-Optimized Output**: Generates structured text content
- **Web Interface**: Easy-to-use React frontend
- **Background Monitoring**: Automated URL monitoring and content change detection
- **Content Change Tracking**: Monitors URLs for updates and regenerates content

## Quick Start

### Local Development
See `LOCAL_DEPLOYMENT.md` for complete local setup instructions.

### Production Deployment
See `RAILWAY_DEPLOYMENT.md` for Railway deployment instructions.

## Documentation

- **Local Deployment**: `LOCAL_DEPLOYMENT.md` - Complete guide for local development with Docker
- **Railway Deployment**: `RAILWAY_DEPLOYMENT.md` - Production deployment on Railway

## Configuration

### Required Environment Variables
- `SECRET_KEY` - Application security key
- `BASE_URL` - Application base URL

### Optional Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `MAX_PAGES` - Maximum pages to crawl (default: 30)
- `MAX_DEPTH` - Crawl depth (default: 1)
- `MONITORING_INTERVAL_MINUTES` - Monitoring interval in minutes (default: 1440 for 24 hours)

## Usage

1. **Add URLs**: Enter website URLs to monitor
2. **Crawl**: The application automatically crawls and analyzes content
3. **View Results**: See AI-categorized and summarized content
4. **Download**: Copy or download the generated LLM text
5. **Monitor Changes**: The system automatically monitors URLs for content changes

## How It Works

### System Architecture
The LLM Text Generator consists of several components working together:

- **Frontend**: React web interface for user interaction
- **Backend**: FastAPI application handling API requests and business logic
- **Database**: SQLite/PostgreSQL for data persistence
- **Crawler**: Playwright-based web crawler for content extraction
- **AI Service**: OpenAI integration for content analysis and summarization
- **Monitor**: Cron-based background service for change detection

### Data Flow
1. **URL Submission**: User submits a URL through the web interface
2. **Initial Crawl**: System crawls the website and extracts content
3. **AI Processing**: OpenAI analyzes and categorizes the content
4. **LLM Text Generation**: Creates structured text optimized for LLMs
5. **Storage**: Content is stored in the database with content hashes
6. **Monitoring**: Cron job periodically checks for content changes
7. **Change Detection**: When content changes, the system regenerates LLM text

### Content Change Monitoring
**Cron Job → Content Re-crawling → Change Detection → Updates**

1. **Cron job triggers** daily at 2 AM
2. **System identifies** URLs to monitor (completed jobs)
3. **Re-crawling** of monitored URLs
4. **Content hash comparison** with previous versions
5. **Change detection** when hashes differ
6. **Automatic regeneration** of LLM text for changed content
7. **Database updates** with new content and timestamps

### Change Detection Algorithm
1. **Content Hashing**: Generate SHA-256 hash of crawled content
2. **Previous Hash**: Retrieve stored hash from database
3. **Comparison**: Compare current hash with previous hash
4. **Change Detection**: If hashes differ, content has changed
5. **Update Process**: Regenerate LLM text and update database

## System Workflows

### 1. Initial URL Processing
```
User submits URL → Frontend → Backend API → Database
                                    ↓
                            FastAPI BackgroundTasks
                                    ↓
                            Background Crawler (Async)
                                    ↓
                            Content Extraction
                                    ↓
                            AI Processing (OpenAI)
                                    ↓
                            LLM Text Generation
                                    ↓
                            Database Storage
```

### 2. Content Change Monitoring
```
Cron Job (Daily 2 AM) → Check Completed Jobs
                              ↓
                        Re-crawl URLs
                              ↓
                        Compare Content Hashes
                              ↓
                        Changes Detected?
                              ↓
                        Regenerate LLM Text
                              ↓
                        Update Database
```

### 3. System Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │  Database   │
│   (React)   │◀──▶│   (FastAPI) │◀──▶│ (SQLite/    │
│             │    │             │    │ PostgreSQL) │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │   Crawler   │
                   │ (Playwright)│
                   └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │   OpenAI    │
                   │   (AI API)  │
                   └─────────────┘
```

## Database Schema

### URLJob Table
```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY,
    url VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    content_hash VARCHAR,
    llm_text_content TEXT,
    error_stack TEXT,
    last_crawled DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    monitoring_enabled BOOLEAN DEFAULT TRUE,
    content_changed BOOLEAN DEFAULT FALSE,
    previous_content_hash VARCHAR,
    progress_percentage INTEGER DEFAULT 0,
    progress_message VARCHAR DEFAULT 'Pending'
);
```

### CrawledPage Table
```sql
CREATE TABLE crawled_pages (
    id INTEGER PRIMARY KEY,
    job_id INTEGER REFERENCES urls(id),
    url VARCHAR NOT NULL,
    title VARCHAR,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Architecture

- **Backend**: FastAPI (Python) with SQLAlchemy
- **Frontend**: React
- **Database**: SQLite (local) or PostgreSQL (production)
- **AI Integration**: OpenAI GPT models for content analysis
- **Web Crawling**: Playwright for JavaScript-heavy sites
- **Reverse Proxy**: Nginx for production deployment

## Development

### Prerequisites
- Docker
- Node.js (for frontend development)
- Python 3.9+ (for backend development)

### Local Development Setup
```bash
# Build and run the application
docker build -t llm-text-generator .
docker run -d -p 80:80 --env-file .env --name llm-text-generator llm-text-generator

# View logs
docker logs -f llm-text-generator

# Stop the application
docker stop llm-text-generator
```

### Making Changes
- **Backend**: Edit files in `backend/app/`
- **Frontend**: Edit files in `frontend/src/`
- **Configuration**: Update `Dockerfile` or environment variables

## API Endpoints

- `GET /` - Frontend application
- `POST /jobs` - Create new monitoring job
- `GET /jobs/{id}` - Get job status and results
- `GET /jobs/{id}/progress` - Get job progress
- `GET /monitor/status` - Check monitoring system status
- `POST /monitor/trigger` - Manually trigger monitoring
