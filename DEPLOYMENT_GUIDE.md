# 🚀 Mind Reader AI - Deployment Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Docker Deployment](#docker-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Start

### Minimum Setup (5 minutes)
```bash
# 1. Clone and setup
git clone <repo>
cd "Mind Reader AI System"
python -m venv .venv
.venv\Scripts\activate  # Windows or source .venv/bin/activate on Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run API
python mind_reader_api_enhanced.py

# 4. Open browser
# http://localhost:5000
```

---

## Local Development

### Complete Setup

#### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Verify activation
python --version  # Should show Python 3.8+
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import flask; print('✅ Flask installed')"
```

#### 3. Configure Environment
```bash
# Create .env file
cat > .env << EOF
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True
JWT_SECRET_KEY=dev-secret-key
DB_TYPE=sqlite
DB_PATH=mind_reader.db
CACHE_SIZE=1000
LOG_LEVEL=INFO
EOF
```

#### 4. Initialize Database
```bash
python << 'EOF'
from database_integration import AnalysisDatabase
db = AnalysisDatabase()
print("✅ Database initialized")
EOF
```

#### 5. Start Development Server
```bash
# With auto-reload
python mind_reader_api_enhanced.py

# Or with Flask development server
export FLASK_APP=mind_reader_api_enhanced.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

#### 6. Test Installation
```bash
# In another terminal
curl http://localhost:5000/api/health

# Should return:
# {"status": "healthy", "timestamp": "...", "version": "2.0"}
```

---

## Production Deployment

### Pre-Deployment Checklist
- [ ] Environment variables configured
- [ ] Database backup created
- [ ] SSL certificates obtained
- [ ] Rate limiting configured
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup strategy defined

### Production Environment Configuration
```env
# .env.production
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False
JWT_SECRET_KEY=<generate-strong-random-key>
JWT_ALGORITHM=HS256

# Database
DB_TYPE=postgresql
DB_HOST=db.example.com
DB_PORT=5432
DB_USER=mindreader
DB_PASSWORD=<strong-password>
DB_NAME=mindreader_prod

# Cache
CACHE_SIZE=10000
CACHE_BACKEND=redis
REDIS_URL=redis://cache.example.com:6379/0

# Security
CORS_ORIGINS=["https://dashboard.example.com"]
HTTPS_ONLY=True
SECURE_COOKIES=True

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/mindreader/api.log
SENTRY_DSN=<your-sentry-project>

# Performance
WORKERS=4
WORKER_TIMEOUT=60
MAX_CONNECTIONS=100
```

### Using Gunicorn (Recommended)

#### Installation
```bash
pip install gunicorn
```

#### Configuration (gunicorn_config.py)
```python
import multiprocessing

# Server
bind = "0.0.0.0:5000"
backlog = 2048
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60

# Logging
accesslog = "/var/log/mindreader/access.log"
errorlog = "/var/log/mindreader/error.log"
loglevel = "warning"

# Process naming
proc_name = "mindreader-api"

# SSL
keyfile = "/etc/ssl/private/mindreader.key"
certfile = "/etc/ssl/certs/mindreader.crt"

# Performance
keepalive = 5
```

#### Run with Gunicorn
```bash
# Basic
gunicorn -w 4 -b 0.0.0.0:5000 mind_reader_api_enhanced:create_app()

# With configuration file
gunicorn -c gunicorn_config.py mind_reader_api_enhanced:create_app()

# With systemd service
sudo systemctl start mindreader-api
```

### Systemd Service (Linux/Mac)

#### Create /etc/systemd/system/mindreader-api.service
```ini
[Unit]
Description=Mind Reader AI API
After=network.target
Wants=mindreader-db.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/mindreader
Environment="PATH=/opt/mindreader/venv/bin"
ExecStart=/opt/mindreader/venv/bin/gunicorn \
    -c /opt/mindreader/gunicorn_config.py \
    mind_reader_api_enhanced:create_app()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable mindreader-api
sudo systemctl start mindreader-api
sudo systemctl status mindreader-api
```

### Nginx Reverse Proxy

#### /etc/nginx/sites-available/mindreader
```nginx
upstream mindreader {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.mindreader.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.mindreader.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/mindreader.crt;
    ssl_certificate_key /etc/ssl/private/mindreader.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Logging
    access_log /var/log/nginx/mindreader_access.log;
    error_log /var/log/nginx/mindreader_error.log;
    
    # Proxy settings
    location / {
        proxy_pass http://mindreader;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://mindreader;
        access_log off;
    }
}
```

#### Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/mindreader \
    /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl restart nginx
```

---

## Cloud Platforms

### AWS Deployment (EC2 + RDS)

#### 1. Launch EC2 Instance
```bash
# Ubuntu 20.04 LTS
# Instance type: t3.medium (minimum)
# Storage: 50GB
# Security group: Allow 80, 443, 22
```

#### 2. Setup Instance
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.9 python3-pip python3-venv git postgresql-client-12

# Create app directory
sudo mkdir -p /opt/mindreader
sudo chown $USER:$USER /opt/mindreader

cd /opt/mindreader
git clone <repo> .
```

#### 3. Create RDS Database
```bash
# MySQL/PostgreSQL
# db.t3.small instance
# 20GB storage
# Enable backups (30 days)
# Multi-AZ enabled for production
```

#### 4. Deploy
```bash
cd /opt/mindreader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env with RDS credentials
# Start with Gunicorn
venv/bin/gunicorn -c gunicorn_config.py mind_reader_api_enhanced:create_app()
```

#### 5. Setup Auto-Scaling (Optional)
```bash
# Create AMI from configured instance
# Setup launch template
# Create Auto Scaling Group (2-10 instances)
# Setup Application Load Balancer
```

### Heroku Deployment

#### 1. Prepare Application
```bash
# Add Procfile
cat > Procfile << EOF
web: gunicorn -w 4 mind_reader_api_enhanced:create_app()
EOF

# Add runtime.txt
echo "python-3.9.16" > runtime.txt
```

#### 2. Deploy
```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create mind-reader-ai

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set JWT_SECRET_KEY=<random-key>
heroku config:set DB_TYPE=postgresql

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### AWS Lambda (Serverless)

#### 1. Prepare for Lambda
```bash
pip install zappa
pip install -r requirements.txt

# Create zappa_settings.json
cat > zappa_settings.json << 'EOF'
{
    "production": {
        "app_function": "mind_reader_api_enhanced.create_app",
        "aws_region": "us-east-1",
        "project_name": "mindreader",
        "runtime": "python3.9",
        "s3_bucket": "mindreader-zappa-deployments",
        "environment_variables": {
            "JWT_SECRET_KEY": "your-secret-key"
        }
    }
}
EOF
```

#### 2. Deploy
```bash
zappa init production
zappa deploy production
zappa tail production --non-http
```

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "mind_reader_api_enhanced:create_app()"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - JWT_SECRET_KEY=dev-key
      - DB_TYPE=postgresql
      - DB_HOST=postgres
      - DB_USER=mindreader
      - DB_PASSWORD=password
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:13-alpine
    environment:
      - POSTGRES_USER=mindreader
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mindreader
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Build and Run
```bash
# Build
docker build -t mindreader-ai:latest .

# Run
docker run -p 5000:5000 -e JWT_SECRET_KEY=secret mindreader-ai:latest

# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check API health
curl -s http://localhost:5000/api/health | jq

# Check database
curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:5000/api/stats/summary

# Monitor performance
watch -n 5 'curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:5000/api/stats/performance | jq'
```

### Logging

#### Centralized Logging (ELK Stack)
```yaml
# docker-compose.yml addition
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
```

### Backup Strategy

#### Daily Backup
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/mindreader"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump mindreader_prod > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://mindreader-backups/

# Keep only 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

#### Schedule with Cron
```bash
# Run daily at 2 AM
0 2 * * * /opt/mindreader/backup.sh
```

### Performance Optimization

#### Database Indexing
```sql
CREATE INDEX idx_analyses_timestamp ON analyses(timestamp DESC);
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_type ON analyses(analysis_type);
```

#### Query Optimization
```bash
# Enable slow query logging
# MySQL
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

### Scaling Strategy

#### Horizontal Scaling
1. Load balancer (Nginx/HAProxy)
2. Multiple API instances
3. Shared database (RDS)
4. Shared cache (Redis)

#### Vertical Scaling
1. Increase instance size
2. Increase worker count
3. Optimize database queries
4. Enable connection pooling

---

## Troubleshooting Deployment

### Issue: Port 5000 Already In Use
```bash
# Find process
lsof -i :5000
# Kill process
kill -9 <PID>
# Or use different port
gunicorn -b 0.0.0.0:8000 mind_reader_api_enhanced:create_app()
```

### Issue: Database Connection Failed
```bash
# Test connection
psql -h db.example.com -U mindreader -d mindreader_prod

# Check credentials in .env
cat .env | grep DB_
```

### Issue: 502 Bad Gateway (Nginx)
```bash
# Check Gunicorn is running
ps aux | grep gunicorn

# Check logs
tail -f /var/log/mindreader/error.log
tail -f /var/log/nginx/error.log

# Restart Gunicorn
sudo systemctl restart mindreader-api
```

### Issue: High Memory Usage
```bash
# Check memory
free -h
ps aux --sort=-%mem | head -n 10

# Reduce Gunicorn workers
gunicorn -w 2 mind_reader_api_enhanced:create_app()

# Monitor with top
watch -n 1 'top -n 1 | head -n 20'
```

---

## Production Checklist

- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting setup
- [ ] Log aggregation enabled
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] JWT secret key strong and secure
- [ ] Environment variables secured
- [ ] Database credentials in secret manager
- [ ] Auto-scaling configured
- [ ] Load balancer health checks enabled
- [ ] Documentation updated
- [ ] Disaster recovery plan created
- [ ] Team training completed

---

**Last Updated:** April 19, 2026  
**Version:** 2.0  
**Status:** ✅ Production Ready
