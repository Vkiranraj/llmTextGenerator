# LLM Text Generator

A powerful web application that crawls websites and generates AI-enhanced, organized text content optimized for Large Language Models (LLMs).

## Features

- **Web Crawling**: Automatically crawls websites up to configurable depth
- **AI Enhancement**: Uses OpenAI for intelligent categorization and summaries
- **LLM-Optimized Output**: Generates structured text content perfect for AI training
- **Web Interface**: Easy-to-use React frontend
- **Background Monitoring**: Automated URL monitoring and updates
- **Email Notifications**: Optional email alerts for monitoring updates

## Quick Start

### Local Development
See `LOCAL_DEPLOYMENT.md` for complete local setup instructions.

### Production Deployment (Railway)
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
- **Frontend**: React with modern UI
- **Database**: SQLite (local) or PostgreSQL (production)
- **AI Integration**: OpenAI GPT models for content analysis
- **Web Crawling**: Playwright for JavaScript-heavy sites
- **Reverse Proxy**: Nginx for production deployment

## Development

### Prerequisites
- Docker and Docker Compose
- Node.js (for frontend development)
- Python 3.9+ (for backend development)

### Local Development Setup
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Making Changes
- **Backend**: Edit files in `backend/app/`
- **Frontend**: Edit files in `frontend/src/`
- **Configuration**: Update `docker-compose.yml` or environment variables

## API Endpoints

- `GET /` - Frontend application
- `POST /jobs` - Create new monitoring job
- `GET /jobs/{id}` - Get job status and results
- `GET /jobs/{id}/progress` - Get job progress
- `POST /unsubscribe` - Unsubscribe from notifications

## Troubleshooting

### Common Issues
1. **Port conflicts**: Change `NGINX_PORT` in `.env`
2. **Docker issues**: Ensure Docker is running and you have permissions
3. **OpenAI errors**: Verify API key and credits
4. **Database issues**: Check database file permissions

### Getting Help
1. Check application logs: `docker-compose logs`
2. Verify environment variables are set correctly
3. Ensure all services are running: `docker-compose ps`
4. Check network connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with Docker
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the documentation files
2. Review the troubleshooting section
3. Check application logs for errors
4. Verify your configuration

## Changelog

### Version 1.0.0
- Initial release
- Web crawling with Playwright
- OpenAI integration for AI enhancement
- React frontend
- Docker containerization
- Railway deployment support
- Email notifications
- Background monitoring
