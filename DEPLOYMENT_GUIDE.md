# 🚀 Deployment Guide - File Conversion Platform

Complete guide for deploying the File Conversion Platform to production environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [External Tools Installation](#external-tools-installation)
4. [Environment Configuration](#environment-configuration)
5. [Development Deployment](#development-deployment)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Security Best Practices](#security-best-practices)
9. [Performance Optimization](#performance-optimization)
10. [Monitoring & Logging](#monitoring--logging)
11. [Backup & Recovery](#backup--recovery)
12. [Scaling Considerations](#scaling-considerations)
13. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Python**: 3.8 or higher (3.11+ recommended)
- **pip**: Latest version
- **Git**: For version control
- **Database**: SQLite (included) or PostgreSQL for production

### Optional Tools (for advanced conversions)
- **FFmpeg**: Audio and video conversions
- **Tesseract OCR**: Text extraction from images
- **LibreOffice**: Advanced document conversions
- **ImageMagick**: Advanced image processing
- **Ghostscript**: PDF operations

### Operating System Support
- ✅ **Linux** (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- ✅ **macOS** (10.15+)
- ✅ **Windows** (10/11, Server 2019+)

---

## 💻 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Disk**: 10 GB free space
- **Network**: 10 Mbps

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB SSD
- **Network**: 100 Mbps+

### Estimated Resource Usage
- **Small files (< 1MB)**: ~50 MB RAM per conversion
- **Medium files (1-10MB)**: ~200 MB RAM per conversion
- **Large files (10-50MB)**: ~500 MB RAM per conversion
- **Video/Audio**: 1-2 GB RAM per conversion

---

## 🛠️ External Tools Installation

### FFmpeg (Audio/Video Conversions)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### CentOS/RHEL
```bash
sudo yum install -y epel-release
sudo yum install -y ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Windows
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

#### Verify Installation
```bash
ffmpeg -version
```

### Tesseract OCR (Text Recognition)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y tesseract-ocr
sudo apt install -y libtesseract-dev

# Install language packs
sudo apt install -y tesseract-ocr-eng  # English
sudo apt install -y tesseract-ocr-spa  # Spanish
sudo apt install -y tesseract-ocr-fra  # French
```

#### CentOS/RHEL
```bash
sudo yum install -y epel-release
sudo yum install -y tesseract
```

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

#### Windows
1. Download installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

#### Verify Installation
```bash
tesseract --version
```

### LibreOffice (Advanced Document Conversions)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y libreoffice
```

#### CentOS/RHEL
```bash
sudo yum install -y libreoffice
```

#### macOS
```bash
brew install --cask libreoffice
```

#### Windows
Download and install from https://www.libreoffice.org/download/

### ImageMagick (Advanced Image Processing)

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y imagemagick
```

#### macOS
```bash
brew install imagemagick
```

#### Windows
Download from https://imagemagick.org/script/download.php

---

## ⚙️ Environment Configuration

### 1. Create Environment File

Create `backend/.env`:

```env
# Application Settings
APP_NAME=File Conversion Platform
APP_VERSION=1.0.0
DEBUG=False

# Server Settings
HOST=0.0.0.0
PORT=8000

# File Settings
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
FILE_RETENTION_HOURS=1

# Database
DATABASE_URL=sqlite:///./conversions.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# External Tools Paths (optional, if not in PATH)
FFMPEG_PATH=/usr/bin/ffmpeg
TESSERACT_PATH=/usr/bin/tesseract
LIBREOFFICE_PATH=/usr/bin/libreoffice

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Background Tasks (if using Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourdomain.com
```

### 2. Generate Secret Key

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output to `SECRET_KEY` in `.env`

### 3. Set Permissions

#### Linux/macOS
```bash
chmod 600 backend/.env
chmod 755 backend/uploads
chmod 755 backend/outputs
```

---

## 🏃 Development Deployment

### Quick Start (Local Development)

#### 1. Clone Repository
```bash
git clone <repository-url>
cd file_conversion
```

#### 2. Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Start Development Server
```bash
# With auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
python -m uvicorn app.main:app --reload
```

#### 5. Access Application
- **Web UI**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🏭 Production Deployment

### Method 1: Systemd Service (Linux)

#### 1. Create Service File

Create `/etc/systemd/system/file-converter.service`:

```ini
[Unit]
Description=File Conversion Platform
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/file_conversion/backend
Environment="PATH=/var/www/file_conversion/backend/venv/bin"
ExecStart=/var/www/file_conversion/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/file_conversion/backend/uploads /var/www/file_conversion/backend/outputs

[Install]
WantedBy=multi-user.target
```

#### 2. Deploy Application
```bash
# Create application directory
sudo mkdir -p /var/www/file_conversion
sudo chown www-data:www-data /var/www/file_conversion

# Copy application files
sudo cp -r . /var/www/file_conversion/
cd /var/www/file_conversion/backend

# Set up virtual environment
sudo -u www-data python -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt

# Create directories
sudo -u www-data mkdir -p uploads outputs logs
sudo chmod 755 uploads outputs logs
```

#### 3. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable file-converter
sudo systemctl start file-converter

# Check status
sudo systemctl status file-converter

# View logs
sudo journalctl -u file-converter -f
```

### Method 2: Gunicorn (Production WSGI Server)

#### 1. Install Gunicorn
```bash
pip install gunicorn
```

#### 2. Create Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Process naming
proc_name = "file_converter"

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
umask = 0
tmp_upload_dir = None

# SSL (if using HTTPS directly)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
```

#### 3. Start with Gunicorn
```bash
gunicorn -c gunicorn_config.py app.main:app
```

### Method 3: Nginx Reverse Proxy

#### 1. Install Nginx
```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

#### 2. Configure Nginx

Create `/etc/nginx/sites-available/file-converter`:

```nginx
upstream file_converter {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 50M;
    client_body_timeout 120s;

    # Logging
    access_log /var/log/nginx/file_converter_access.log;
    error_log /var/log/nginx/file_converter_error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Static files
    location /static {
        alias /var/www/file_conversion/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to FastAPI
    location / {
        proxy_pass http://file_converter;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://file_converter;
    }
}
```

#### 3. Enable Configuration
```bash
sudo ln -s /etc/nginx/sites-available/file-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. SSL Certificate (Let's Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libreoffice \
    imagemagick \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .
COPY frontend/ ./static

# Create directories
RUN mkdir -p uploads outputs logs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - MAX_FILE_SIZE_MB=50
      - DATABASE_URL=postgresql://postgres:password@db:5432/fileconverter
      - CELERY_BROKER_URL=redis://redis:6379/0
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/outputs:/app/outputs
      - ./backend/logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=fileconverter
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/usr/share/nginx/html:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` files to version control
- ✅ Use strong, unique secret keys
- ✅ Rotate secrets regularly
- ✅ Use different secrets for dev/staging/production

### 2. File Upload Security
```python
# backend/app/config.py additions
ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'jpg', 'png', 'mp3', 'mp4'  # Whitelist only
}

MAX_FILE_SIZE_MB = 50  # Strict limit
SCAN_UPLOADS = True  # Enable virus scanning (if available)
```

### 3. Rate Limiting
```python
# Aggressive rate limiting for production
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_HOUR = 50
RATE_LIMIT_PER_DAY = 200
```

### 4. Input Validation
- ✅ Validate all file extensions
- ✅ Check MIME types
- ✅ Sanitize filenames
- ✅ Reject suspicious files

### 5. Network Security
```bash
# Firewall rules (Ubuntu/Debian)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Block direct access to application port
sudo ufw deny 8000/tcp
```

### 6. Logging & Monitoring
```python
# Log all uploads and conversions
LOG_UPLOADS = True
LOG_CONVERSIONS = True
LOG_ERRORS = True
LOG_SECURITY_EVENTS = True
```

### 7. Database Security
```bash
# PostgreSQL security
# 1. Use strong passwords
# 2. Restrict network access
# 3. Enable SSL connections
# 4. Regular backups
# 5. Keep updated
```

---

## ⚡ Performance Optimization

### 1. Caching Strategy

```python
# Install Redis
pip install redis

# Configure caching
REDIS_URL = "redis://localhost:6379"
CACHE_TTL = 3600  # 1 hour
```

### 2. Background Tasks (Celery)

```bash
# Install Celery
pip install celery redis

# Start worker
celery -A app.celery worker --loglevel=info

# Start beat (periodic tasks)
celery -A app.celery beat --loglevel=info
```

### 3. Database Optimization

```sql
-- PostgreSQL indexes
CREATE INDEX idx_conversions_status ON conversions(status);
CREATE INDEX idx_conversions_created ON conversions(created_at);
CREATE INDEX idx_conversions_ip ON conversions(ip_address);
```

### 4. File System Optimization

```bash
# Use tmpfs for temporary files (Linux)
sudo mount -t tmpfs -o size=2G tmpfs /var/www/file_conversion/backend/uploads
```

### 5. Load Balancing

```nginx
# Nginx load balancing
upstream file_converter {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-client
pip install python-json-logger
```

### 2. Log Rotation

Create `/etc/logrotate.d/file-converter`:

```
/var/www/file_conversion/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload file-converter
    endscript
}
```

### 3. Health Checks

```bash
# Automated health check
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart file-converter
```

---

## 💾 Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/backups/fileconverter"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump fileconverter > "$BACKUP_DIR/db_$DATE.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql" -mtime +30 -delete
```

### File Backup

```bash
# Backup uploads and outputs
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ outputs/
```

---

## 📈 Scaling Considerations

### Horizontal Scaling
1. Load balancer (Nginx/HAProxy)
2. Multiple application servers
3. Shared file storage (NFS/S3)
4. Distributed cache (Redis Cluster)
5. Database replication (PostgreSQL)

### Vertical Scaling
1. Increase CPU cores
2. Add more RAM
3. Use SSD storage
4. Optimize worker processes

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Application won't start
```bash
# Check logs
sudo journalctl -u file-converter -n 50

# Check port availability
sudo netstat -tlnp | grep 8000

# Check permissions
ls -la /var/www/file_conversion/backend
```

**Issue**: File conversions failing
```bash
# Check external tools
which ffmpeg tesseract libreoffice

# Check disk space
df -h

# Check memory
free -h
```

**Issue**: High memory usage
```bash
# Reduce worker processes
# Edit gunicorn_config.py
workers = 2  # Reduce from 4

# Monitor memory
watch -n 1 free -h
```

---

**Production Ready! 🎉**

*Last Updated: January 2026*
