# Production Deployment Checklist

## Overview
This document lists all the configurations needed to run your Django application in production mode with Gunicorn + Nginx, PostgreSQL, Redis, Celery, and remote SeaweedFS.

---

## ✅ Completed Configurations

### 1. **Gunicorn Configuration** ✅
- **File**: `gunicorn.conf.py`
- **Features**:
  - Auto-calculated workers based on CPU cores
  - Worker recycling (prevents memory leaks)
  - Proper timeouts and graceful shutdown
  - Logging with lifecycle hooks
  - Preload app for better memory efficiency

**Documentation**: See `docs/gunicorn-configuration.md`

---

### 2. **Nginx Configuration** ✅
- **File**: `nginx.conf`
- **Features**:
  - Optimized static file serving
  - Media file proxy with caching (30-day cache)
  - Gzip compression
  - Security headers (X-Frame-Options, XSS Protection, etc.)
  - Rate limiting (10 req/s general, 5 req/min admin)
  - Connection limiting
  - 100MB upload limit
  - WebSocket support removed (not needed)

**Documentation**: See `docs/nginx-configuration.md`

---

### 3. **Environment Variables** ✅
- **File**: `.env.prod`
- **Fixed**:
  - `ENVIRONMENT=production` (triggers Gunicorn in entrypoint.sh)
  - `DJANGO_ALLOWED_HOSTS` (required for DEBUG=False)
  - `DJANGO_CSRF_TRUSTED_ORIGINS` (for CSRF protection)
  - `DJANGO_SECRET_KEY` (production secret)
  - PostgreSQL connection variables
  - Redis connection variables
  - SeaweedFS URL

---

### 4. **PostgreSQL Database** ✅
- **Configuration**: Environment variables in `.env.prod`
- **Note**: Currently using remote PostgreSQL at `100.84.214.91:5432`
- **Docker**: Not included in `docker-compose.prod.yml` (using remote DB)

---

### 5. **Redis** ✅
- **Configuration**: Included in `docker-compose.yml`
- **Features**:
  - Password authentication
  - Health checks
  - Volume for data persistence

---

### 6. **Celery** ✅
- **Configuration**: Worker, Beat, and Flower services in `docker-compose.yml`
- **Features**:
  - Celery Worker (async tasks)
  - Celery Beat (scheduled tasks)
  - Flower (monitoring UI on port 5555)

---

### 7. **SeaweedFS Storage** ✅
- **Configuration**: Custom storage backend (`apps/blog/storage.py`)
- **Features**:
  - Remote storage at `100.84.214.91:8888`
  - Custom Django storage backend
  - Nginx caching for media files (reduces load)
  - 30-day Nginx cache, 7-day browser cache

---

## 📋 Required Environment Variables

### **`.env.prod` (Production Environment)**

```bash
# Database Configuration
POSTGRES_DB=your_production_db
POSTGRES_USER=your_production_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_HOST=100.84.214.91  # or your PostgreSQL host
POSTGRES_PORT=5432

# Django Configuration
ENVIRONMENT=production
DJANGO_SECRET_KEY=your-very-long-random-secret-key-change-this
DJANGO_SETTINGS_MODULE=config.settings.production

# Security Settings
DJANGO_ALLOWED_HOSTS=yourdomain.com,your-tailscale-name.ts.net,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://your-tailscale-name.ts.net
DJANGO_INTERNAL_IPS=172.20.0.1

# Superuser (optional - for auto-creation)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=secure_password

# GitHub Integration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
GITHUB_BASE_URL=https://api.github.com
GITHUB_API_VERSION=2022-11-28

# Redis Configuration
REDIS_PASSWORD=your_redis_password
REDIS_HOST=redis  # Docker service name
REDIS_PORT=6379
REDIS_DB_INDEX=0

# Celery Configuration
CELERY_BROKER_REDIS_DB_INDEX=1
CELERY_BACKEND_REDIS_DB_INDEX=2

# Flower Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=secure_flower_password

# Discord Bot (optional)
DISCORD_BOT_TOKEN=your_discord_bot_token

# SeaweedFS Storage
SEAWEEDFS_URL=http://100.84.214.91:8888
```

---

## 🚀 Deployment Commands

### **Development Mode**
```bash
docker compose up -d --build
```

### **Production Mode**
```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### **Stop Services**
```bash
docker compose down
```

### **View Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django
docker compose logs -f nginx-proxy
docker compose logs -f celery-worker
```

---

## 🔧 Docker Compose Configuration

### **Add Nginx Cache Volume**

Update `docker-compose.prod.yml`:

```yaml
services:
  nginx-proxy:
    image: nginx:latest
    container_name: django-blog-nginx-container
    ports:
      - "8001:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - nginx_cache:/var/cache/nginx  # Add this
    depends_on:
      - django

volumes:
  static_volume:
  nginx_cache:  # Add this
```

This persists Nginx media cache across container restarts.

---

## 🧪 Testing Production Setup

### **1. Test Gunicorn**
```bash
# Check if Gunicorn is running
docker exec django-blog-container ps aux | grep gunicorn

# Should show:
# - 1 master process
# - Multiple worker processes (CPU cores × 2 + 1)
```

### **2. Test Nginx**
```bash
# Test config syntax
docker exec django-blog-nginx-container nginx -t

# Check Nginx is serving
curl -I http://localhost:8001/

# Test static files
curl -I http://localhost:8001/static/css/output.css

# Test media file caching
curl -I http://localhost:8001/trungstacks-blog-media/your-file.jpg
# Look for: X-Cache-Status: HIT or MISS
```

### **3. Test Database Connection**
```bash
docker exec -it django-blog-container poetry run python manage.py dbshell
# Should connect to PostgreSQL
```

### **4. Test Redis Connection**
```bash
docker exec -it django-redis-container redis-cli -a your_redis_password ping
# Should return: PONG
```

### **5. Test Celery Worker**
```bash
docker logs django-celery-worker-container
# Should show: "celery@worker ready"
```

### **6. Test Flower (Celery Monitoring)**
```bash
# Access in browser
http://localhost:5555
# Login with FLOWER_USER and FLOWER_PASSWORD
```

### **7. Test SeaweedFS**
```bash
# Upload test file through Django admin
# Check if file is accessible
curl -I http://100.84.214.91:8888/trungstacks-blog-media/test.jpg
```

---

## 🔒 Security Checklist

### **Before Going Live:**

- [ ] Change `DJANGO_SECRET_KEY` to a strong random value
- [ ] Update `DJANGO_ALLOWED_HOSTS` with your actual domain
- [ ] Update `DJANGO_CSRF_TRUSTED_ORIGINS` with your domain (with https://)
- [ ] Change `DJANGO_SUPERUSER_PASSWORD` to a strong password
- [ ] Change `REDIS_PASSWORD` to a strong password
- [ ] Change `FLOWER_PASSWORD` to a strong password
- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Review and update `GITHUB_PERSONAL_ACCESS_TOKEN` permissions
- [ ] Set up HTTPS via Tailscale (already configured)
- [ ] Review Nginx rate limits and adjust if needed
- [ ] Enable Django security settings (already in production.py)
- [ ] Set up database backups
- [ ] Set up log monitoring
- [ ] Configure error tracking (Sentry, etc.)

---

## 📊 Monitoring

### **Application Logs**
```bash
# Django application
docker logs -f django-blog-container

# Nginx access logs
docker exec django-blog-nginx-container tail -f /var/log/nginx/access.log

# Nginx error logs
docker exec django-blog-nginx-container tail -f /var/log/nginx/error.log
```

### **Performance Monitoring**
```bash
# Docker stats (CPU, memory usage)
docker stats

# Nginx cache size
docker exec django-blog-nginx-container du -sh /var/cache/nginx/media

# Redis info
docker exec django-redis-container redis-cli -a your_password info stats
```

### **Celery Monitoring**
- Access Flower UI: `http://localhost:5555`
- View task history, success/failure rates
- Monitor worker health

---

## 🐛 Troubleshooting

### **CommandError: You must set settings.ALLOWED_HOSTS if DEBUG is False**
**Fix**: Set `DJANGO_ALLOWED_HOSTS` in `.env.prod`:
```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1
```

### **502 Bad Gateway from Nginx**
**Causes**:
1. Django/Gunicorn not running
2. Wrong upstream configuration
3. Django crashed

**Fix**:
```bash
docker logs django-blog-container  # Check Django logs
docker restart django-blog-container
```

### **Static files not loading**
**Fix**:
```bash
# Rebuild static files
docker exec django-blog-container poetry run python manage.py collectstatic --no-input
docker restart django-blog-nginx-container
```

### **Media files returning 404**
**Causes**:
1. File doesn't exist in SeaweedFS
2. Wrong URL being generated
3. Nginx cache issue

**Fix**:
```bash
# Test direct SeaweedFS access
curl -I http://100.84.214.91:8888/trungstacks-blog-media/your-file.jpg

# Clear Nginx cache
docker exec django-blog-nginx-container rm -rf /var/cache/nginx/media/*
docker restart django-blog-nginx-container
```

### **Database connection errors**
**Fix**:
```bash
# Check PostgreSQL is accessible
docker exec django-blog-container nc -zv 100.84.214.91 5432

# Verify environment variables
docker exec django-blog-container env | grep POSTGRES
```

### **Redis connection errors**
**Fix**:
```bash
# Check Redis is running
docker ps | grep redis

# Test connection
docker exec django-redis-container redis-cli -a your_password ping
```

---

## 📚 Documentation References

- [Gunicorn Configuration Guide](./gunicorn-configuration.md)
- [Nginx Configuration Guide](./nginx-configuration.md)
- [Useful Commands](./usefull-command.md)

---

## 🎯 Next Steps

1. **Update `.env.prod`** with your actual values:
   - Domain name
   - Strong passwords
   - Actual database credentials

2. **Test locally** with production setup:
   ```bash
   docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build
   ```

3. **Configure Tailscale** for SSL/TLS

4. **Deploy to production server**

5. **Set up monitoring and backups**

---

## ✅ Summary

Your Django application is now configured with:
- ✅ Gunicorn for production WSGI serving
- ✅ Nginx for reverse proxy and static/media file serving
- ✅ PostgreSQL database (remote)
- ✅ Redis for caching and Celery broker
- ✅ Celery for async tasks
- ✅ SeaweedFS for media storage with Nginx caching
- ✅ Comprehensive security headers
- ✅ Rate limiting and connection limits
- ✅ Gzip compression
- ✅ Optimized caching strategy

**You're production-ready!** 🚀
