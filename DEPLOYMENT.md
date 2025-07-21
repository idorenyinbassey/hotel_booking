# 🚀 Hotel Booking System - Deployment Guide

This guide covers production deployment of the Hotel Booking System using Docker, cloud services, and best practices for scaling and monitoring.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS / Windows 10+
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 20GB+ available space
- **Network**: Stable internet connection

### Required Software
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.25+
- **SSL Certificate**: For HTTPS (Let's Encrypt recommended)

## 🔧 Environment Configuration

### 1. Clone Repository
```bash
git clone https://github.com/idorenyinbassey/hotel_booking.git
cd hotel_booking
```

### 2. Environment Variables
Create production environment file:
```bash
cp .env.example .env.prod
```

Edit `.env.prod` with production values:
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hotel_booking_prod
DB_USER=hotel_user
DB_PASSWORD=secure-database-password
DB_HOST=postgres
DB_PORT=5432

# Redis Cache
REDIS_URL=redis://redis:6379/1
CACHE_TTL=300

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Stripe Payment
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Elasticsearch
ELASTICSEARCH_HOST=elasticsearch:9200
ELASTICSEARCH_INDEX=hotel_booking

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
```

## 🐳 Docker Production Setup

### 1. Production Docker Compose
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    volumes:
      - ./static:/app/static
      - ./media:/app/media
    env_file:
      - .env.prod
    depends_on:
      - postgres
      - redis
      - elasticsearch
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=hotel_booking_prod
      - POSTGRES_USER=hotel_user
      - POSTGRES_PASSWORD=secure-database-password
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hotel_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx1g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A hotel_booking worker -l info
    volumes:
      - ./media:/app/media
    env_file:
      - .env.prod
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A hotel_booking beat -l info
    env_file:
      - .env.prod
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
      - ./media:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

### 2. Production Dockerfile
Create `Dockerfile.prod`:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=hotel_booking.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hotel_booking.wsgi:application"]
```

### 3. Nginx Configuration
Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream web {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 30d;
        }

        # API rate limiting
        location /api/auth/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://web;
            include proxy_params;
        }

        location /api/ {
            limit_req zone=api burst=200 nodelay;
            proxy_pass http://web;
            include proxy_params;
        }

        # Main application
        location / {
            proxy_pass http://web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## ☁️ Cloud Deployment Options

### AWS Deployment

#### 1. ECS (Elastic Container Service)
```yaml
# ecs-task-definition.json
{
    "family": "hotel-booking",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "1024",
    "memory": "2048",
    "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "web",
            "image": "your-registry/hotel-booking:latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "DEBUG", "value": "False"},
                {"name": "DB_HOST", "value": "your-rds-endpoint"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/hotel-booking",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
```

#### 2. Required AWS Services
- **RDS**: PostgreSQL database
- **ElastiCache**: Redis cluster
- **Elasticsearch Service**: Search functionality
- **ALB**: Application Load Balancer
- **Route 53**: DNS management
- **CloudFront**: CDN for static files
- **S3**: Static and media file storage

### Google Cloud Platform

#### 1. Cloud Run Deployment
```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hotel-booking
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cloudsql-instances: PROJECT:REGION:INSTANCE
    spec:
      containers:
      - image: gcr.io/PROJECT/hotel-booking:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "False"
        - name: DB_HOST
          value: "127.0.0.1"  # Cloud SQL Proxy
        resources:
          limits:
            cpu: 1
            memory: 2Gi
```

### DigitalOcean App Platform

```yaml
# .do/app.yaml
name: hotel-booking
services:
- name: web
  source_dir: /
  github:
    repo: idorenyinbassey/hotel_booking
    branch: main
  run_command: gunicorn --bind 0.0.0.0:8000 hotel_booking.wsgi:application
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-s
  env:
  - key: DEBUG
    value: "False"
  - key: DATABASE_URL
    type: SECRET
  - key: REDIS_URL
    type: SECRET

databases:
- name: hotel-db
  engine: PG
  num_nodes: 1
  size: basic-xs
  version: "15"
```

## 🗄️ Database Migration

### Production Migration Steps
```bash
# 1. Create database backup
docker-compose exec postgres pg_dump -U hotel_user hotel_booking_prod > backup.sql

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# 5. Update search index
docker-compose exec web python manage.py search_index --rebuild
```

## 🔒 Security Checklist

### SSL/TLS Configuration
- [ ] SSL certificate installed (Let's Encrypt recommended)
- [ ] Force HTTPS redirects
- [ ] Strong SSL ciphers configured
- [ ] HSTS headers enabled

### Django Security
- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` properly configured
- [ ] Security middleware enabled
- [ ] CSRF protection enabled
- [ ] Secure cookie settings

### Database Security
- [ ] Strong database passwords
- [ ] Database user with limited permissions
- [ ] Database network isolation
- [ ] Regular automated backups

### Infrastructure Security
- [ ] Firewall configured (only necessary ports open)
- [ ] Regular security updates
- [ ] Log monitoring and alerting
- [ ] Rate limiting configured
- [ ] DDoS protection enabled

## 📊 Monitoring & Logging

### 1. Application Monitoring (Sentry)
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

### 2. System Monitoring (Docker)
```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. Log Aggregation
```yaml
  elasticsearch-logging:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch-logging
```

## 🚀 Deployment Commands

### Initial Deployment
```bash
# 1. Clone and setup
git clone https://github.com/idorenyinbassey/hotel_booking.git
cd hotel_booking

# 2. Configure environment
cp .env.example .env.prod
# Edit .env.prod with production values

# 3. Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Run initial setup
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py search_index --rebuild

# 5. Verify deployment
curl https://yourdomain.com/health/
```

### Updates & Maintenance
```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Database backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U hotel_user hotel_booking_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

## 📈 Performance Optimization

### 1. Database Optimization
- Connection pooling with `django-db-connection-pool`
- Query optimization and indexing
- Read replica configuration
- Database query caching

### 2. Caching Strategy
- Redis for session and query caching
- CDN for static assets
- Browser caching headers
- API response caching

### 3. Application Optimization
- Gunicorn with multiple workers
- Async task processing with Celery
- Database connection pooling
- Static file compression

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: |
        # Your deployment script here
        docker-compose -f docker-compose.prod.yml up -d --build
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database connectivity
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell

# Reset database connections
docker-compose -f docker-compose.prod.yml restart postgres
```

#### 2. Static Files Not Loading
```bash
# Recollect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --clear --noinput

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### 3. Redis Connection Issues
```bash
# Test Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Clear Redis cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli flushall
```

### Health Check Endpoints
- **Application**: `https://yourdomain.com/health/`
- **Database**: `https://yourdomain.com/health/db/`
- **Redis**: `https://yourdomain.com/health/cache/`
- **API**: `https://yourdomain.com/api/health/`

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- [ ] **Daily**: Monitor logs and alerts
- [ ] **Weekly**: Database backups verification
- [ ] **Monthly**: Security updates and patches
- [ ] **Quarterly**: Performance review and optimization

### Emergency Contacts
- **Infrastructure**: your-devops@company.com
- **Application**: your-dev-team@company.com
- **Database**: your-dba@company.com

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Security Guide](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

**Successfully deployed! Your Hotel Booking System is now ready for production use.** 🎉
