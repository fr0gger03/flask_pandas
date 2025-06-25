# Production Deployment Guide for Flask Workload Parser

This guide documents all necessary changes to implement a production-ready deployment with Redis, Nginx, Gunicorn, and Sentry monitoring.

## Overview

The production setup includes:
- **Gunicorn**: Production WSGI server
- **Redis**: Session storage and caching
- **Nginx**: Reverse proxy and static file serving
- **Sentry**: Error monitoring and logging
- **PostgreSQL**: Production database
- **Docker**: Containerized deployment

## Required Files and Changes

### 1. Production Dependencies (`pyproject.toml`)

Add a production dependency group to your existing `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "flask-testing>=0.8.1",
    "pytest>=8.4.0",
    "pytest-flask>=1.3.0",
    "testcontainers[postgres]>=4.10.0",
]
prod = [
    "gunicorn>=21.2.0",
    "redis>=5.0.1",
    "sentry-sdk[flask]>=1.38.0",
]
```

### 2. Production Environment File (`.env.production`)

Create a production environment configuration:

```bash
# Production Environment Configuration
# Copy this to .env and update with your actual values

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
# Use PostgreSQL for production
POSTGRES_PASSWORD=secure-production-password
DATABASE_URL=postgresql://inventorydbuser:secure-production-password@db:5432/inventorydb

# Security
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600

# File Upload Configuration
UPLOAD_FOLDER=/app/input
MAX_CONTENT_LENGTH=104857600  # 100MB

# Redis Configuration (for sessions and caching)
REDIS_URL=redis://redis:6379/0
SESSION_TYPE=redis
SESSION_REDIS_URL=redis://redis:6379/0
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
SESSION_KEY_PREFIX=workload_parser:

# Sentry Configuration (for error monitoring)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s %(levelname)s %(name)s %(message)s

# Server Configuration
SERVER_NAME=your-domain.com
PREFERRED_URL_SCHEME=https
```

### 3. Production Dockerfile (`Dockerfile.production`)

Create a production-optimized container:

```dockerfile
# Production Dockerfile for Flask Workload Parser

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PATH="/app/.venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (base + production group)
RUN uv sync --frozen --group prod

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Create necessary directories
RUN mkdir -p /app/input /app/logs && \
    chown -R app:app /app

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run gunicorn with Flask app factory pattern
CMD ["uv", "run", "gunicorn", "--config", "gunicorn.conf.py", "parser.app:create_app()"]
```

### 4. Gunicorn Configuration (`gunicorn.conf.py`)

Create Gunicorn server configuration:

```python
# Gunicorn configuration file for Flask Workload Parser

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'flask-workload-parser'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment variables
raw_env = [
    'FLASK_ENV=production',
]
```

### 5. Nginx Configuration (`nginx.conf`)

Create reverse proxy configuration:

```nginx
# Nginx configuration for Flask Workload Parser
# Place this in /etc/nginx/sites-available/flask-workload-parser
# and symlink to /etc/nginx/sites-enabled/

upstream flask_app {
    server app:8000;
    # Add more servers for load balancing if needed
    # server app2:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # File upload size limit
    client_max_body_size 100M;
    
    # Static files
    location /static {
        alias /app/parser/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        alias /app/parser/static/favicon.ico;
        expires 1y;
        access_log off;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Main application
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Buffer settings for large uploads
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Logging
    access_log /var/log/nginx/flask-workload-parser.access.log;
    error_log /var/log/nginx/flask-workload-parser.error.log;
}

# HTTPS redirect (uncomment when you have SSL certificates)
# server {
#     listen 80;
#     server_name your-domain.com www.your-domain.com;
#     return 301 https://$server_name$request_uri;
# }

# HTTPS configuration (uncomment and configure when you have SSL certificates)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com www.your-domain.com;
#     
#     ssl_certificate /path/to/your/certificate.crt;
#     ssl_certificate_key /path/to/your/private.key;
#     
#     # SSL configuration
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#     
#     # Include the location blocks from above here
# }
```

### 6. Production Docker Compose (`docker-compose.prod.yml`)

Create multi-service production stack:

```yaml
services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: workload_parser_db
    environment:
      POSTGRES_DB: inventorydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./parser/sql:/docker-entrypoint-initdb.d
    networks:
      - app_network
    restart: unless-stopped
    healthcheck:
      test: [ "CMD", "pg_isready", "-U", "inventorydbuser", "-d", "inventorydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for sessions and caching
  redis:
    image: redis:7-alpine
    container_name: workload_parser_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask Application
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: workload_parser_app
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - SENTRY_DSN=${SENTRY_DSN}
      - UPLOAD_FOLDER=/app/input
    volumes:
      - app_input:/app/input
      - app_logs:/app/logs
    networks:
      - app_network
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: workload_parser_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - nginx_logs:/var/log/nginx
      - app_input:/app/input:ro  # Read-only access for serving uploaded files
      # Uncomment for SSL certificates
      # - ./ssl:/etc/ssl/certs
    networks:
      - app_network
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  app_input:
  app_logs:
  nginx_logs:

networks:
  app_network:
    driver: bridge
```

### 7. Flask Application Updates

#### Add health check endpoint to `routes.py`:

```python
@bp.route("/health")
def health():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}, 200
```

#### Update Flask app configuration for production (`config.py`):

Add Redis and Sentry configuration:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    SESSION_TYPE = 'redis'
    SESSION_REDIS_URL = os.getenv('SESSION_REDIS_URL', 'redis://localhost:6379/0')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'workload_parser:'
    
    # Sentry configuration
    SENTRY_DSN = os.getenv('SENTRY_DSN')

class ProductionConfig(Config):
    DEBUG = False
    # Additional production-specific settings
```

#### Update `app.py` to include Redis and Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_session import Session
import redis

def create_app(config=None):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    
    # Initialize Sentry (only in production)
    if app.config.get('SENTRY_DSN') and app.config.get('FLASK_ENV') == 'production':
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )
    
    # Initialize Redis for sessions
    if app.config.get('REDIS_URL'):
        app.config['SESSION_REDIS'] = redis.from_url(app.config['REDIS_URL'])
        Session(app)
    
    # Rest of your existing app initialization...
    db.init_app(app)
    # ... etc
    
    return app
```

## Deployment Instructions

### 1. Prerequisites

- Docker and Docker Compose installed
- Domain name configured (for production)
- SSL certificates (optional but recommended)
- Sentry account and DSN (for error monitoring)

### 2. Environment Setup

1. Copy `.env.production` to `.env`
2. Update all placeholder values with your actual configuration:
   - `SECRET_KEY`: Generate a secure random key
   - `POSTGRES_PASSWORD`: Set a strong database password
   - `SENTRY_DSN`: Your Sentry project DSN
   - `SERVER_NAME`: Your actual domain name

### 3. Build and Deploy

```bash
# Regenerate lock file with production dependencies
uv lock

# Build and start production stack
docker compose -f docker-compose.prod.yml --env-file .env up --build -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check service health
docker compose -f docker-compose.prod.yml ps
```

### 4. SSL Setup (Optional but Recommended)

1. Obtain SSL certificates (Let's Encrypt, purchased, etc.)
2. Update `nginx.conf` to enable HTTPS configuration
3. Mount certificate files in docker-compose.prod.yml
4. Restart nginx service

### 5. Monitoring and Maintenance

- Monitor logs: `docker compose -f docker-compose.prod.yml logs -f app`
- Check health endpoints: `curl http://your-domain.com/health`
- Monitor Sentry dashboard for errors
- Set up log rotation for nginx and application logs

## Security Considerations

1. **Never use default passwords in production**
2. **Enable HTTPS with valid SSL certificates**
3. **Regularly update Docker images and dependencies**
4. **Use a firewall to restrict access to necessary ports only**
5. **Monitor logs and set up alerting**
6. **Backup database regularly**
7. **Use environment variables for all secrets**

## Scaling Considerations

- Add more app containers behind nginx for load balancing
- Use external Redis cluster for session storage
- Configure database connection pooling
- Set up monitoring with Prometheus/Grafana
- Use container orchestration (Kubernetes) for larger deployments

## Troubleshooting

Common issues and solutions:

1. **Database connection failed**: Check POSTGRES_PASSWORD and DATABASE_URL
2. **502 Bad Gateway**: Check if app container is healthy and accessible
3. **File upload issues**: Verify UPLOAD_FOLDER permissions and nginx file size limits
4. **Session issues**: Check Redis connectivity and configuration
5. **SSL issues**: Verify certificate paths and nginx configuration

This guide provides a complete production-ready setup that is scalable, secure, and maintainable.
