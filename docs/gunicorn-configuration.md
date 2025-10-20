# Gunicorn Configuration Guide

## Overview

Gunicorn (Green Unicorn) is a Python WSGI HTTP Server for UNIX that serves your Django application in production. This guide explains the configuration used in this project.

---

## Current Configuration

### Location
- Configuration file: `gunicorn.conf.py` (project root)
- Called from: `entrypoint.sh` when `ENVIRONMENT=production`

### Command
```bash
poetry run gunicorn config.wsgi:application --config gunicorn.conf.py
```

---

## Configuration Settings Explained

### 1. Server Socket
```python
bind = "0.0.0.0:8000"
backlog = 2048
```
- **bind**: Listen on all network interfaces, port 8000
- **backlog**: Maximum number of pending connections (queue size)

### 2. Worker Processes
```python
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
```
- **workers**: Number of worker processes
  - Formula: `(CPU cores × 2) + 1`
  - 4-core CPU = 9 workers
  - 2-core CPU = 5 workers
- **worker_class**: Type of worker
  - `sync`: Synchronous workers (default, good for most Django apps)
  - `gevent`: Async workers (for I/O-bound apps)
  - `gthread`: Threaded workers
- **worker_connections**: Max simultaneous clients per worker (for async workers)

### 3. Worker Lifecycle
```python
max_requests = 1000
max_requests_jitter = 50
timeout = 120
graceful_timeout = 30
keepalive = 5
```
- **max_requests**: Restart worker after N requests (prevents memory leaks)
- **max_requests_jitter**: Add randomness to prevent all workers restarting at once
- **timeout**: Kill workers that don't respond within N seconds
- **graceful_timeout**: Time to wait for workers to finish during shutdown
- **keepalive**: Seconds to wait for next request on Keep-Alive connection

### 4. Performance Optimization
```python
worker_tmp_dir = "/dev/shm"
preload_app = True
```
- **worker_tmp_dir**: Use RAM (`/dev/shm`) for temporary files instead of disk
- **preload_app**: Load application code before forking workers
  - ✅ Faster startup time
  - ✅ Less memory usage (shared memory)
  - ⚠️ Code changes require server restart

### 5. Logging
```python
accesslog = "-"      # stdout
errorlog = "-"       # stderr
loglevel = "info"
capture_output = True
```
- **accesslog**: HTTP access logs (use `-` for stdout, Docker captures this)
- **errorlog**: Error logs (use `-` for stderr)
- **loglevel**: Log verbosity (`debug`, `info`, `warning`, `error`, `critical`)
- **capture_output**: Capture stdout/stderr from application

### 6. Process Management
```python
proc_name = "django-blog"
daemon = False
pidfile = None
```
- **proc_name**: Process name shown in `ps` and `top`
- **daemon**: Run in background (False for Docker containers)
- **pidfile**: File to store master process ID (not needed in Docker)

---

## Worker Class Comparison

| Worker Class | Best For | Pros | Cons |
|--------------|----------|------|------|
| **sync** (default) | CPU-bound tasks, traditional Django | Simple, reliable, predictable | Blocking I/O |
| **gevent** | I/O-bound, many concurrent connections | High concurrency, efficient | Requires gevent library, complex debugging |
| **gthread** | Mixed workload, moderate concurrency | Threading support, good balance | Python GIL limitations |
| **eventlet** | Similar to gevent | High concurrency | Requires eventlet library |

### When to Use Each:

#### Use **sync** (current) if:
- ✅ Traditional Django views
- ✅ Database-heavy operations
- ✅ Simple request/response cycle
- ✅ Easy to debug

#### Use **gevent** if:
- 🔄 Many concurrent WebSocket connections
- 🔄 Heavy external API calls
- 🔄 Long-polling requests
- 🔄 Real-time applications

#### Use **gthread** if:
- 🔀 Mix of I/O and CPU-bound tasks
- 🔀 Need threading for background tasks
- 🔀 Moderate concurrency requirements

---

## Calculating Optimal Workers

### Formula
```
workers = (2 × CPU_cores) + 1
```

### Examples
| CPU Cores | Workers | Max Concurrent Requests |
|-----------|---------|-------------------------|
| 1 core    | 3       | 3 |
| 2 cores   | 5       | 5 |
| 4 cores   | 9       | 9 |
| 8 cores   | 17      | 17 |

### Memory Considerations
Each worker uses ~100-300MB of RAM:
- 4 workers × 200MB = ~800MB minimum
- Add buffer for spikes: 1.5GB recommended

### Testing Your Configuration
```bash
# Check memory usage per worker
docker stats

# Monitor worker processes
docker exec -it django-blog-container ps aux | grep gunicorn

# Test concurrent requests
ab -n 1000 -c 10 http://localhost:8000/
```

---

## Production Best Practices

### 1. Use Preload App
```python
preload_app = True
```
✅ Saves memory by sharing code between workers
⚠️ Requires restart on code changes

### 2. Set Request Limits
```python
max_requests = 1000
max_requests_jitter = 50
```
✅ Prevents memory leaks
✅ Automatic worker recycling

### 3. Configure Timeouts Properly
```python
timeout = 120           # Kill stuck workers
graceful_timeout = 30   # Allow graceful shutdown
```
✅ Adjust based on your longest request time
⚠️ Set timeout > longest expected request

### 4. Use RAM for Temp Files
```python
worker_tmp_dir = "/dev/shm"
```
✅ Faster than disk
⚠️ Ensure `/dev/shm` has enough space

### 5. Log to stdout/stderr
```python
accesslog = "-"
errorlog = "-"
```
✅ Docker/Kubernetes friendly
✅ Easy log aggregation

---

## Troubleshooting

### Issue: Workers dying frequently
**Symptoms**: `Worker timeout` errors
**Solutions**:
- Increase `timeout` value
- Check for slow database queries
- Optimize view performance
- Check memory usage

### Issue: High memory usage
**Symptoms**: OOM errors, container restarts
**Solutions**:
- Reduce number of workers
- Lower `max_requests` to recycle workers more often
- Enable `preload_app = True`
- Profile memory usage

### Issue: Slow response times
**Symptoms**: High latency under load
**Solutions**:
- Increase number of workers
- Consider switching to `gevent` for I/O-bound apps
- Add caching (Redis)
- Optimize database queries

### Issue: Connection errors
**Symptoms**: `502 Bad Gateway` from Nginx
**Solutions**:
- Check if workers are running: `ps aux | grep gunicorn`
- Verify bind address matches Nginx proxy_pass
- Increase `backlog` value
- Check worker logs for crashes

---

## Performance Tuning

### Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| Workers | 2-3 | `(CPU × 2) + 1` |
| Worker Class | sync | sync or gevent |
| Timeout | 60s | 120s |
| Max Requests | 0 (unlimited) | 1000-5000 |
| Preload App | False | True |
| Log Level | debug | info or warning |

### Load Testing
```bash
# Install Apache Bench
brew install apache-bench  # macOS
apt install apache2-utils  # Ubuntu

# Test with 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8000/

# Test with POST data
ab -n 100 -c 10 -p post.json -T application/json http://localhost:8000/api/

# Monitor during test
watch -n 1 'docker stats --no-stream'
```

---

## Advanced Configuration

### SSL/TLS Termination (if not using Nginx)
```python
# In gunicorn.conf.py
keyfile = "/path/to/key.pem"
certfile = "/path/to/cert.pem"
```

### Custom Server Hooks
```python
def on_starting(server):
    """Called before master process initialization"""
    print("Server starting...")

def when_ready(server):
    """Called after server is ready"""
    print(f"Server ready with {server.cfg.workers} workers")

def pre_fork(server, worker):
    """Called before worker is forked"""
    pass

def post_fork(server, worker):
    """Called after worker is forked"""
    print(f"Worker {worker.pid} spawned")

def worker_exit(server, worker):
    """Called when worker exits"""
    print(f"Worker {worker.pid} exited")
```

### Graceful Reloads
```bash
# Send HUP signal to reload
docker exec django-blog-container kill -HUP 1

# Or use Docker
docker exec django-blog-container poetry run gunicorn config.wsgi:application --reload
```

---

## Monitoring

### Health Check Endpoint
Add to your Django app:
```python
# urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"})

urlpatterns = [
    path('health/', health_check),
]
```

### Prometheus Metrics (Optional)
```bash
# Install prometheus client
poetry add prometheus-client

# Add to gunicorn.conf.py
from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
```

---

## References

- [Gunicorn Official Documentation](https://docs.gunicorn.org/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Gunicorn Design](https://docs.gunicorn.org/en/stable/design.html)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Gunicorn Best Practices](https://pythonspeed.com/articles/gunicorn-in-docker/)
