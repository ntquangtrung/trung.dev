# Nginx Configuration Guide

## Overview

Nginx is configured as a reverse proxy in front of your Django application (via Gunicorn). It handles static files, SSL/TLS (via Tailscale), rate limiting, and forwards dynamic requests to Django.

---

## Architecture

```
Internet → Tailscale (SSL/TLS) → Nginx (Port 80) → Gunicorn (Port 8000) → Django
                                    ↓
                                Static Files (direct serve)
```

---

## Configuration Location

- **Config File**: `nginx.conf` (project root)
- **Container**: `nginx-proxy` service in `docker-compose.prod.yml`
- **Mounted as**: `/etc/nginx/nginx.conf` inside container

---

## Key Features

### 1. **Static File Serving**
Nginx serves static files directly without hitting Django:
```nginx
location /static/ {
    alias /app/staticfiles/;
    expires 1y;  # Cache for 1 year
}
```

**Benefits**:
- ✅ 10-100x faster than Django serving
- ✅ Reduces Django/Gunicorn load
- ✅ Browser caching enabled
- ✅ Gzip compression applied

### 2. **Gzip Compression**
Compresses text-based responses:
```nginx
gzip on;
gzip_comp_level 6;
gzip_types text/css application/javascript ...;
```

**Results**:
- ✅ 70-90% size reduction for text files
- ✅ Faster page loads
- ✅ Lower bandwidth costs

### 3. **Rate Limiting**
Protects against abuse and DDoS:
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
```

**Zones**:
- **general**: 10 requests/second for normal pages
- **api**: 100 requests/second for API endpoints
- **login**: 5 requests/minute for admin/login

### 4. **Security Headers**
Protects against common attacks:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### 5. **Upload Limits**
Allows file uploads up to 100MB:
```nginx
client_max_body_size 100M;
```

**Without this**: Default is 1MB, uploads fail with `413 Request Entity Too Large`

---

## Configuration Sections Explained

### Worker Processes
```nginx
worker_processes auto;
worker_rlimit_nofile 8192;
```
- **worker_processes**: Auto-detects CPU cores and creates that many workers
- **worker_rlimit_nofile**: Max open files per worker (handles many connections)

### Events Block
```nginx
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}
```
- **worker_connections**: Max connections per worker (1024 × workers = total capacity)
- **use epoll**: Linux-specific efficient event processing
- **multi_accept**: Accept multiple connections at once

### Performance Settings
```nginx
sendfile on;
tcp_nopush on;
tcp_nodelay on;
keepalive_timeout 65;
```
- **sendfile**: Efficient file sending (kernel-level)
- **tcp_nopush**: Send headers and file in one packet
- **tcp_nodelay**: Don't buffer small packets
- **keepalive_timeout**: Keep connections open for reuse

### Open File Cache
```nginx
open_file_cache max=1000 inactive=20s;
open_file_cache_valid 30s;
```
- Caches file descriptors for static files
- Reduces disk I/O for frequently accessed files

### Upstream Backend
```nginx
upstream django_backend {
    server django:8000;
    keepalive 32;
}
```
- Defines Django backend server
- **keepalive 32**: Maintains 32 persistent connections to Gunicorn

---

## Location Blocks Breakdown

### Static Files
```nginx
location /static/ {
    alias /app/staticfiles/;
    expires 1y;
    access_log off;
}
```
**Purpose**: Serve CSS, JS, images directly  
**Caching**: 1 year (use Django's `ManifestStaticFilesStorage` for cache busting)

### Media Files
```nginx
location /media/ {
    alias /app/mediafiles/;
    expires 7d;
}
```
**Purpose**: Serve user-uploaded files (avatars, attachments)  
**Caching**: 7 days

### Health Checks
```nginx
location /health/ {
    access_log off;
    proxy_pass http://django_backend;
}
```
**Purpose**: Monitoring endpoint (no rate limiting, no logging)

### Admin Panel
```nginx
location /admin/ {
    limit_req zone=login burst=5 nodelay;
    proxy_read_timeout 300s;
}
```
**Purpose**: Django admin with stricter rate limiting  
**Timeout**: 5 minutes for long-running admin operations

### API Endpoints
```nginx
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```
**Purpose**: API endpoints with higher rate limits

### All Other Requests
```nginx
location / {
    limit_req zone=general burst=20 nodelay;
    proxy_pass http://django_backend;
}
```
**Purpose**: Forward everything else to Django

---

## Rate Limiting Deep Dive

### How It Works
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
```
- **$binary_remote_addr**: Track by IP address
- **zone=general:10m**: 10MB memory for tracking IPs (~160,000 IPs)
- **rate=10r/s**: Allow 10 requests per second

### Burst Configuration
```nginx
limit_req zone=general burst=20 nodelay;
```
- **burst=20**: Allow temporary burst of 20 extra requests
- **nodelay**: Process burst requests immediately (don't queue)

### Rate Limit Zones

| Zone | Rate | Burst | Use Case |
|------|------|-------|----------|
| **general** | 10/s | 20 | Normal page views |
| **api** | 100/s | 20 | API endpoints |
| **login** | 5/m | 5 | Login/admin access |

### Customizing Rates
Edit the zones to match your traffic:
```nginx
# More relaxed
limit_req_zone $binary_remote_addr zone=general:10m rate=50r/s;

# Stricter
limit_req_zone $binary_remote_addr zone=general:10m rate=5r/s;
```

---

## Security Best Practices

### 1. Hide Nginx Version
```nginx
server_tokens off;
```
Prevents attackers from knowing your Nginx version.

### 2. Deny Hidden Files
```nginx
location ~ /\. {
    deny all;
}
```
Prevents access to `.git`, `.env`, etc.

### 3. Connection Limits
```nginx
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;
```
Max 10 simultaneous connections per IP.

### 4. Security Headers
| Header | Purpose |
|--------|---------|
| `X-Frame-Options` | Prevent clickjacking |
| `X-Content-Type-Options` | Prevent MIME sniffing |
| `X-XSS-Protection` | Enable browser XSS filter |
| `Referrer-Policy` | Control referrer information |

---

## Performance Tuning

### Calculating Worker Capacity
```
Max Connections = worker_processes × worker_connections
```

**Example**:
- 4 CPU cores → 4 worker processes
- 1024 connections each
- **Total capacity**: 4,096 concurrent connections

### Memory Considerations
- Each worker uses ~10-20MB RAM
- 4 workers ≈ 40-80MB for Nginx
- Very lightweight compared to Django

### Optimizing for High Traffic
```nginx
worker_processes auto;
worker_connections 2048;  # Increase if needed
keepalive_requests 1000;  # More requests per connection
keepalive_timeout 30;     # Reduce if memory is tight
```

---

## Monitoring & Debugging

### Check Nginx Status
```bash
# Inside container
docker exec -it django-blog-nginx-container nginx -t  # Test config
docker exec -it django-blog-nginx-container nginx -s reload  # Reload config
```

### View Logs
```bash
# Access logs
docker logs django-blog-nginx-container

# Follow logs in real-time
docker logs -f django-blog-nginx-container
```

### Test Rate Limiting
```bash
# Hammer endpoint to trigger rate limit
for i in {1..100}; do curl http://localhost:8001/; done

# Expected: 429 Too Many Requests after ~20 requests
```

### Common Issues

#### Issue: 413 Request Entity Too Large
**Solution**: Increase `client_max_body_size`

#### Issue: 502 Bad Gateway
**Solutions**:
1. Check if Gunicorn is running: `docker logs django-blog-container`
2. Check upstream: `proxy_pass http://django:8000;`
3. Check network: `docker network inspect simple-django-blog_default`

#### Issue: 504 Gateway Timeout
**Solution**: Increase timeouts:
```nginx
proxy_connect_timeout 90s;
proxy_send_timeout 90s;
proxy_read_timeout 90s;
```

#### Issue: Static files not loading
**Solutions**:
1. Check volume mount: `docker inspect django-blog-nginx-container`
2. Verify path: `docker exec -it django-blog-nginx-container ls /app/staticfiles`
3. Check permissions

---

## Integration with Tailscale

Since Tailscale handles SSL/TLS:
- ✅ Nginx listens on HTTP (port 80) only
- ✅ Tailscale terminates SSL before reaching Nginx
- ✅ No need for SSL certificates in Nginx config
- ✅ `$scheme` will be `http`, but Tailscale serves `https`

### Forwarding HTTPS Info
If Django needs to know the original protocol:
```nginx
proxy_set_header X-Forwarded-Proto https;  # Force HTTPS
```

Or in Django settings:
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## Advanced Features

### WebSocket Support
Already included in main location block:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```
Supports WebSocket connections for real-time features.

### Custom Error Pages
```nginx
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;

location = /404.html {
    root /app/staticfiles/error_pages/;
}
```

### IP Whitelisting (Admin)
```nginx
location /admin/ {
    allow 10.0.0.0/8;      # Allow Tailscale network
    allow 192.168.1.0/24;  # Allow local network
    deny all;              # Deny everyone else
}
```

### Caching with Nginx
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_key $scheme$host$request_uri;
}
```

---

## Load Testing

### Using Apache Bench
```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8001/

# Test specific endpoint
ab -n 100 -c 5 http://localhost:8001/blog/

# Test with authentication
ab -n 100 -c 5 -C "sessionid=abc123" http://localhost:8001/admin/
```

### Using wrk
```bash
# Install wrk
brew install wrk  # macOS

# Run test
wrk -t4 -c100 -d30s http://localhost:8001/
```

### Interpreting Results
- **Requests/sec**: Higher is better (aim for >1000/s for static files)
- **Latency**: Lower is better (aim for <100ms for dynamic pages)
- **Failed requests**: Should be 0

---

## Production Checklist

Before deploying:
- [ ] Set appropriate `client_max_body_size` for your app
- [ ] Adjust rate limits based on expected traffic
- [ ] Test all location blocks (static, media, API, admin)
- [ ] Verify gzip compression is working
- [ ] Check security headers with [Security Headers](https://securityheaders.com/)
- [ ] Test file upload functionality
- [ ] Monitor logs for errors
- [ ] Set up log rotation
- [ ] Test health check endpoint
- [ ] Verify Tailscale integration

---

## Useful Commands

```bash
# Reload Nginx config without downtime
docker exec django-blog-nginx-container nginx -s reload

# Test config syntax
docker exec django-blog-nginx-container nginx -t

# View running processes
docker exec django-blog-nginx-container ps aux

# Check listening ports
docker exec django-blog-nginx-container netstat -tlnp

# View cache size
docker exec django-blog-nginx-container du -sh /var/cache/nginx

# Clear cache
docker exec django-blog-nginx-container rm -rf /var/cache/nginx/*
```

---

## References

- [Nginx Official Documentation](https://nginx.org/en/docs/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/)
- [Security Headers](https://securityheaders.com/)
- [Django with Nginx](https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/gunicorn/#nginx)
