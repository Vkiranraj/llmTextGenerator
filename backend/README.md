# LLM Text Generator Backend

A FastAPI-based backend service for crawling websites and generating LLM text content. The service monitors URLs for content changes and automatically updates content when changes are detected.

## Features

- **URL Crawling**: Crawl websites with configurable depth and page limits
- **AI Enhancement**: OpenAI integration for intelligent categorization and summaries
- **LLM Text Generation**: Extract and process content for LLM consumption
- **Content Monitoring**: Track content changes over time using content hashing
- **Automated Updates**: Automatically regenerate content when changes are detected
- **RESTful API**: Complete API for job management
- **Database Storage**: SQLite/PostgreSQL support
- **Single Container**: All services in one Docker container
- **Cron Monitoring**: Automated background monitoring with configurable intervals

## Quick Start

### API Access
The backend provides a RESTful API for URL monitoring and LLM text generation:

- **Base URL**: `http://localhost:8000` (local) or `https://your-app.railway.app` (production)
- **API Documentation**: `/docs` (Swagger UI)
- **Health Check**: `/` endpoint

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../env.example .env
# Edit .env with your settings

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Docker (single container)
docker build -t llm-text-generator .
docker run -d -p 80:80 --env-file .env --name llm-text-generator llm-text-generator

# Railway
railway up
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/docs` | API documentation |
| `GET` | `/jobs/` | List all jobs |
| `POST` | `/jobs/` | Create new job |
| `GET` | `/jobs/{job_id}` | Get job details |
| `GET` | `/jobs/{job_id}/progress` | Get job progress |
| `GET` | `/jobs/{job_id}/download` | Download job content |

### Job Management

#### Create Job
```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### Get Job Status
```bash
curl "http://localhost:8000/jobs/1"
```

#### Download Content
```bash
curl "http://localhost:8000/jobs/1/download" -o content.txt
```

### Monitoring Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/monitor/status` | Check monitoring system status |
| `POST` | `/monitor/trigger` | Manually trigger monitoring |
| `GET` | `/debug/config` | View configuration values |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./url_monitor.db` | Database connection string |
| `BASE_URL` | `http://localhost:8000` | Application base URL |
| `SECRET_KEY` | `your-secret-key` | Secret key for encryption |
| `MONITORING_INTERVAL_MINUTES` | `1440` | Monitoring interval in minutes |

### OpenAI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | | OpenAI API key for AI features |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | `500` | Maximum tokens for responses |
| `OPENAI_TEMPERATURE` | `0.3` | Response randomness (0-1) |

### Crawling Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_PAGES` | `20` | Maximum pages to crawl |
| `MAX_DEPTH` | `1` | Maximum crawl depth |
| `MAX_CONTENT_PARAGRAPHS` | `10` | Max paragraphs for LLM processing |
| `REQUESTS_TIMEOUT` | `10` | HTTP request timeout (seconds) |
| `PLAYWRIGHT_TIMEOUT` | `60000` | Playwright timeout (milliseconds) |
| `GRACE_PERIOD_CRAWLS` | `2` | Grace period before deleting pages |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   └── config.py         # Configuration management
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # CRUD operations
│   ├── database.py          # Database connection
│   ├── crawler.py           # Web crawling logic
│   ├── openai_service.py    # OpenAI integration
│   ├── email_utils.py       # Email functionality
│   └── helper.py            # Utility functions
├── scripts/
│   └── monitor_urls.py      # URL monitoring script
├── data/                    # SQLite database storage
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## Database Models

### Job
- `id`: Primary key
- `url`: Target URL
- `status`: Job status (pending, processing, completed, error)
- `llm_text_content`: Generated LLM text
- `content_hash`: Content hash for change detection
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_crawled`: Last crawl timestamp
- `error_stack`: Error details if failed

### CrawledPage
- `id`: Primary key
- `job_id`: Associated job
- `url`: Page URL
- `title`: Page title
- `content`: Page content
- `created_at`: Creation timestamp

## Monitoring

### Automatic Monitoring
- **Schedule**: Runs daily at 2 AM via cron job
- **Change Detection**: Uses content hashing to detect modifications
- **Automatic Updates**: Regenerates LLM text when changes detected
- **Database Updates**: Updates job status and content in database

### Manual Monitoring
```bash
# Run monitoring manually
python scripts/monitor_urls.py

# View monitoring logs
tail -f logs/monitor.log
```

## Development

### Running Tests
```bash
# Run the monitoring script manually
python scripts/monitor_urls.py
```

### Database Management
```bash
# Access database (if SQLite)
sqlite3 data/url_monitor.db

# View jobs
SELECT * FROM jobs;
```

### Logs
- **Application logs**: `logs/app.log`
- **Monitoring logs**: `logs/monitor.log`
- **Docker logs**: `docker logs llm-text-generator`

## Deployment

The backend service can be deployed in multiple environments:

### Docker Deployment
```bash
# Single container (includes backend, frontend, nginx, monitor)
docker build -t llm-text-generator .
docker run -d -p 80:80 --env-file .env --name llm-text-generator llm-text-generator
```

### Railway Deployment
1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy with `railway up`
4. Configure domain in Railway settings

### Local Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
All configuration is handled through environment variables:
- **Local**: Use `.env` file
- **Docker**: Use `--env-file .env` flag
- **Railway**: Set in Railway dashboard
- **Production**: Railway dashboard values override local settings

## API Documentation

The API provides automatic documentation:
- **Swagger UI**: http://localhost/api/docs (if enabled)
- **ReDoc**: http://localhost/api/redoc (if enabled)

Note: API documentation is optional and can be disabled for production deployments.

## Troubleshooting

### Common Issues

1. **Database Connection**: Check `DATABASE_URL` setting
2. **Crawling Timeouts**: Adjust `PLAYWRIGHT_TIMEOUT`
3. **Memory Issues**: Reduce `MAX_PAGES` setting
4. **Monitoring Issues**: Check cron job status and logs

### Health Checks
```bash
# Check API health
curl http://localhost:8000/

# Check job status
curl http://localhost:8000/jobs/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
