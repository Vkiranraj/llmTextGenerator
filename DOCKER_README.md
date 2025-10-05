# 🐳 LLM Text Generator - Docker Deployment

This guide will help you deploy the LLM Text Generator application using Docker containers.

## 📋 Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 2GB of available RAM
- At least 5GB of available disk space

## 🚀 Quick Start

### 1. Clone and Deploy

```bash
# Clone the repository
git clone <your-repo-url>
cd llmTextGenerator

# Make scripts executable
chmod +x docker-deploy.sh docker-stop.sh docker-logs.sh

# Deploy the application
./docker-deploy.sh
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

The application consists of three Docker services:

### Backend Service
- **Container**: `llm-text-generator-backend`
- **Port**: 8000
- **Technology**: FastAPI + Python 3.9
- **Features**: URL crawling, LLM text generation, API endpoints

### Frontend Service
- **Container**: `llm-text-generator-frontend`
- **Port**: 3000
- **Technology**: React + Node.js 18
- **Features**: User interface, job management, real-time updates

### Monitor Service
- **Container**: `llm-text-generator-monitor`
- **Technology**: Python + Cron
- **Features**: Automated URL monitoring, content change detection

## 📊 Service Management

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
./docker-logs.sh

# Specific service
./docker-logs.sh backend
./docker-logs.sh frontend
./docker-logs.sh monitor
```

### Stop Services
```bash
./docker-stop.sh
```

### Restart Services
```bash
docker-compose restart
```

## 🔍 Monitoring Features

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

## 📁 Data Persistence

### Database
- **Location**: `./backend/data/url_monitor.db`
- **Type**: SQLite database
- **Persistence**: Survives container restarts

### Generated Files
- **Location**: `./backend/llms_*.txt`
- **Content**: Generated LLM text files
- **Persistence**: Survives container restarts

### Logs
- **Location**: `./backend/logs/`
- **Files**: `monitor.log`, application logs
- **Persistence**: Survives container restarts

## 🛠️ Development

### Build Individual Services
```bash
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
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Monitor container
docker-compose exec monitor bash
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string
- `MAX_PAGES`: Maximum pages to crawl per URL
- `MAX_DEPTH`: Maximum crawl depth
- `MAX_CONTENT_PARAGRAPHS`: Maximum content paragraphs to extract

### Port Configuration
- **Frontend**: 3000 (configurable in docker-compose.yml)
- **Backend**: 8000 (configurable in docker-compose.yml)

## 🚨 Troubleshooting

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
curl http://localhost:8000/
curl http://localhost:3000/
```

## 📈 Performance

### Resource Requirements
- **CPU**: 2 cores minimum, 4 cores recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB minimum, 10GB recommended

### Optimization
- Use SSD storage for better database performance
- Allocate sufficient RAM for Playwright browser instances
- Monitor disk space for generated files

## 🔒 Security

### Network Security
- Services communicate through Docker internal network
- Only necessary ports exposed to host
- No external database dependencies

### Data Security
- SQLite database with file-based storage
- No sensitive data in environment variables
- Logs contain no sensitive information

## 📝 Logs

### Log Locations
- **Application Logs**: `docker-compose logs`
- **Monitoring Logs**: `./backend/logs/monitor.log`
- **Container Logs**: `docker logs <container-name>`

### Log Rotation
```bash
# Set up log rotation (optional)
sudo logrotate -f /etc/logrotate.conf
```

## 🎯 Production Deployment

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

## 🆘 Support

### Getting Help
1. Check the logs: `./docker-logs.sh`
2. Verify service status: `docker-compose ps`
3. Test endpoints: `curl http://localhost:8000/`
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

🎉 **You're all set!** Your LLM Text Generator is now running in Docker containers with automated monitoring.
