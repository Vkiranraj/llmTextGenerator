# LLM Text Generator

A web application that crawls websites and generates AI-enhanced, organized text content optimized for Large Language Models (LLMs).

## Features

- **Web Crawling**: Automatically crawls websites up to configurable depth
- **AI Enhancement**: Uses OpenAI for intelligent categorization and summaries
- **LLM-Optimized Output**: Generates structured text content
- **Web Interface**: Easy-to-use React frontend
- **Background Monitoring**: Automated URL monitoring and updates
- **Email Notifications**: Optional email alerts for monitoring updates

## Quick Start

### Local Development
See `LOCAL_DEPLOYMENT.md` for complete local setup instructions.

### Production Deployment
See `RAILWAY_DEPLOYMENT.md` for Railway deployment instructions.

## Documentation

- **Local Deployment**: `LOCAL_DEPLOYMENT.md` - Complete guide for local development
- **Railway Deployment**: `RAILWAY_DEPLOYMENT.md` - Production deployment on Railway

## Configuration

### Required Environment Variables
- `SECRET_KEY` - Application security key
- `BASE_URL` - Application base URL

### Optional Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `MAX_PAGES` - Maximum pages to crawl (default: 30)
- `MAX_DEPTH` - Crawl depth (default: 1)
- Email configuration for notifications

## Usage

1. **Add URLs**: Enter website URLs to monitor
2. **Crawl**: The application automatically crawls and analyzes content
3. **View Results**: See AI-categorized and summarized content
4. **Download**: Copy or download the generated LLM text

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
- `POST /unsubscribe` - Unsubscribe from notifications
