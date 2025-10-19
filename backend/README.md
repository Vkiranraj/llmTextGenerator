# LLM Text Generator Backend

A FastAPI-based backend service for crawling websites and generating LLM text content. The service monitors URLs for content changes and provides email notifications.

## Features

- **URL Crawling**: Crawl websites with configurable depth and page limits
- **AI Enhancement**: OpenAI integration for intelligent categorization and summaries
- **LLM Text Generation**: Extract and process content for LLM consumption
- **Content Monitoring**: Track content changes over time
- **Email Notifications**: Send alerts when content changes
- **RESTful API**: Complete API for job management
- **Database Storage**: SQLite/PostgreSQL support
- **Single Container**: All services in one Docker container

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
  -d '{"url": "https://example.com", "email": "user@example.com"}'
```

#### Get Job Status
```bash
curl "http://localhost:8000/jobs/1"
```

#### Download Content
```bash
curl "http://localhost:8000/jobs/1/download" -o content.txt
```

### Email Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/subscribe` | Subscribe to URL updates |
| `GET` | `/unsubscribe` | Unsubscribe from updates |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./url_monitor.db` | Database connection string |
| `BASE_URL` | `http://localhost:8000` | Application base URL |
| `SECRET_KEY` | `your-secret-key` | Secret key for encryption |
| `ENCRYPTION_KEY` | | Email token encryption key |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | | SMTP username |
| `SMTP_PASSWORD` | | SMTP password |
| `FROM_EMAIL` | `noreply@example.com` | Sender email address |

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
- `status`: Job status (pending, processing, completed, error, updated)
- `llm_text_content`: Generated LLM text
- `content_hash`: Content hash for change detection
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_crawled`: Last crawl timestamp
- `error_stack`: Error details if failed

### EmailSubscription
- `id`: Primary key
- `job_id`: Associated job
- `email`: Subscriber email
- `created_at`: Subscription timestamp

## Monitoring

### Automatic Monitoring
- Runs daily at 2 AM via cron job
- Checks for content changes
- Sends email notifications
- Updates job status

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
2. **Email Notifications**: Verify SMTP credentials
3. **Crawling Timeouts**: Adjust `PLAYWRIGHT_TIMEOUT`
4. **Memory Issues**: Reduce `MAX_PAGES` setting

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
