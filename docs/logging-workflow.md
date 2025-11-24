# Logging Architecture & Workflow

**Author:** Trung-Dev Team  
**Last Updated:** November 20, 2025  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [Log Flow](#log-flow)
5. [Development Workflow](#development-workflow)
6. [Production Workflow](#production-workflow)
7. [Configuration Details](#configuration-details)
8. [Querying Logs](#querying-logs)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

This Django blog application uses a **centralized logging stack** based on **Grafana Loki** for aggregating, storing, and visualizing logs from all services (Django, Celery, Nginx, Redis, Postgres).

### Why This Stack?

- ✅ **Lightweight**: Loki uses ~500MB RAM (vs 2GB+ for ELK)
- ✅ **Docker-native**: Reads logs directly from Docker containers
- ✅ **Cost-effective**: Free and open-source
- ✅ **Production-ready**: Used by major companies
- ✅ **Easy to query**: LogQL is similar to PromQL (Prometheus)

### Key Features

- **Structured logging**: JSON format in production, human-readable in development
- **Automatic rotation**: Prevents disk space issues
- **Real-time streaming**: View logs as they happen
- **Advanced filtering**: Query by service, container, log level, custom fields
- **Retention policies**: 7 days (dev) / 30 days (prod)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Containers                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌────────┐  ┌───────┐  ┌────────┐  ┌──────────┐│
│  │  Django  │  │ Celery │  │ Nginx │  │ Redis  │  │ Postgres ││
│  │          │  │ Worker │  │       │  │        │  │          ││
│  └────┬─────┘  └───┬────┘  └───┬───┘  └───┬────┘  └────┬─────┘│
│       │            │           │          │            │       │
│       │ stdout/    │ stdout/   │ stdout/  │ stdout/    │ stdout/│
│       │ stderr     │ stderr    │ stderr   │ stderr     │ stderr │
│       ▼            ▼           ▼          ▼            ▼       │
└───────┼────────────┼───────────┼──────────┼────────────┼───────┘
        │            │           │          │            │
        └────────────┴───────────┴──────────┴────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Docker Logging Driver      │
              │   (json-file)                │
              │                              │
              │ Stores logs on host:         │
              │ /var/lib/docker/containers/  │
              │                              │
              │ Max size: 10-50MB per file   │
              │ Max files: 3-5 per container │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │        Promtail              │
              │   (Log Collector)            │
              │                              │
              │ - Watches Docker containers  │
              │ - Parses JSON logs           │
              │ - Adds labels (service, env) │
              │ - Streams to Loki            │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │          Loki                │
              │   (Log Aggregation)          │
              │                              │
              │ - Stores logs (7-30 days)    │
              │ - Indexes by labels          │
              │ - Provides query API         │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │        Grafana               │
              │   (Visualization)            │
              │                              │
              │ - Web UI (port 4000)         │
              │ - LogQL queries              │
              │ - Pre-built dashboards       │
              │ - Real-time streaming        │
              └──────────────────────────────┘
```

---

## Components

### 1. Django Application Logging

**File:** `config/settings/production.py`

```python
LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "apps.blog": {"handlers": ["console"], "level": "INFO"},
        "services": {"handlers": ["console"], "level": "INFO"},
        "celery": {"handlers": ["console"], "level": "INFO"},
    },
}
```

**Output Format (Production):**
```json
{
  "asctime": "2025-11-20T10:30:45.123Z",
  "name": "apps.blog.views",
  "levelname": "INFO",
  "message": "Post viewed",
  "pathname": "/app/apps/blog/views.py",
  "lineno": 42,
  "funcName": "get_object",
  "post_id": 15,
  "user_id": 1
}
```

### 2. Docker Logging Driver

**File:** `docker-compose.prod.yml`

```yaml
services:
  django:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"      # Rotate after 10MB
        max-file: "3"        # Keep 3 files (30MB total)
        labels: "service=django,environment=production,app=trung-dev"
```

**Storage Location:**
```
/var/lib/docker/containers/<container-id>/<container-id>-json.log
/var/lib/docker/containers/<container-id>/<container-id>-json.log.1
/var/lib/docker/containers/<container-id>/<container-id>-json.log.2
```

### 3. Promtail (Log Collector)

**File:** `promtail-config.yaml`

```yaml
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: label
            values: ["com.docker.compose.project=simple-django-blog"]
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container_name'
      - source_labels: ['__meta_docker_container_label_environment']
        target_label: 'environment'
    pipeline_stages:
      - json:
          expressions:
            level: levelname
            logger: name
            message: message
      - labels:
          level:
          logger:
```

**What it does:**
- Auto-discovers Docker containers in the `simple-django-blog` project
- Extracts labels from container metadata
- Parses JSON logs (production)
- Streams logs to Loki every 5 seconds

### 4. Loki (Log Storage)

**File:** `loki-config.prod.yaml`

```yaml
limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 720h  # 30 days
  ingestion_rate_mb: 32
  ingestion_burst_size_mb: 64

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days
```

**Features:**
- **Label-based indexing**: Fast queries by service, container, environment
- **Compression**: Efficient storage using gzip
- **Retention**: Automatic deletion of old logs
- **API**: HTTP API for querying (port 3100)

### 5. Grafana (Visualization)

**File:** `docker-compose.logging.prod.yml`

```yaml
grafana:
  image: grafana/grafana:10.2.3
  ports:
    - "4000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
```

**Features:**
- Web UI at `http://localhost:4000`
- Pre-configured Loki datasource
- 4 pre-built log panels
- LogQL query interface

---

## Log Flow

### Detailed Flow Diagram

```
1. Application Code
   └─> logger.info("Post viewed", extra={"post_id": 15})

2. Django Logging Framework
   └─> Formats log using JsonFormatter
   └─> Outputs to stdout

3. Docker Runtime
   └─> Captures stdout/stderr
   └─> Writes to /var/lib/docker/containers/<id>/<id>-json.log
   └─> Auto-rotates when size > 10MB (production)

4. Promtail
   └─> Watches /var/lib/docker/containers (via Docker API)
   └─> Reads new log lines
   └─> Parses JSON structure
   └─> Extracts labels (container_name, service, environment)
   └─> Streams to Loki HTTP API (http://loki:3100/loki/api/v1/push)

5. Loki
   └─> Receives log stream
   └─> Indexes by labels (not content)
   └─> Compresses and stores chunks
   └─> Deletes logs older than retention period

6. Grafana
   └─> User queries via LogQL
   └─> Grafana sends query to Loki API
   └─> Loki returns matching logs
   └─> Grafana displays in UI
```

### Example: Viewing an Error Log

**Step 1:** Django code raises exception
```python
try:
    result = risky_operation()
except Exception as e:
    logger.exception("Operation failed", extra={"operation": "upload_file"})
```

**Step 2:** JSON log written to stdout
```json
{
  "asctime": "2025-11-20T10:45:30.123Z",
  "name": "apps.blog.views",
  "levelname": "ERROR",
  "message": "Operation failed",
  "operation": "upload_file",
  "exc_info": "Traceback (most recent call last)..."
}
```

**Step 3:** Docker captures and stores
```
/var/lib/docker/containers/abc123.../abc123-json.log
```

**Step 4:** Promtail reads and sends to Loki with labels
```
{container_name="django-blog-container", service="django", environment="production", level="ERROR"}
```

**Step 5:** Query in Grafana
```logql
{service="django", level="ERROR"} | json
```

**Step 6:** View in Grafana UI
```
2025-11-20 10:45:30  ERROR  Operation failed
  operation: upload_file
  exc_info: Traceback...
```

---

## Development Workflow

### Setup

1. **Start logging stack:**
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.logging.dev.yml up -d --build
```

2. **Access Grafana:**
```bash
open http://localhost:4000
# Login: admin / admin
```

3. **Generate logs:**
```bash
# Trigger Django activity
curl http://localhost:8000

# View in terminal
docker compose logs -f django

# Or view in Grafana Explore
```

### Development Configuration

**Log Format:** Human-readable (verbose)
```
INFO 2025-11-20 10:30:45 apps.blog.views PostDetailView Post viewed
```

**Retention:**
- Docker logs: 50MB × 5 files = 250MB per container
- Loki: 7 days
- Total storage: ~2GB for all services (1 week)

**Services:**
- Django: 250MB
- Celery Worker: 250MB
- Postgres: 250MB
- Nginx: N/A (not in dev)
- Redis: 60MB
- Loki: ~500MB
- Grafana: ~100MB

### Common Development Tasks

**1. View live Django logs:**
```bash
docker compose logs -f django
```

**2. Search for errors:**
```bash
docker compose logs django | grep ERROR
```

**3. Export logs for debugging:**
```bash
mkdir -p logs
docker compose logs django > logs/debug-$(date +%Y%m%d-%H%M%S).log
```

**4. Query in Grafana:**
```logql
{container_name="django-blog-container"} |= "ERROR"
```

**5. Reset log data:**
```bash
docker compose down
docker volume rm simple-django-blog_loki-dev-data
docker compose up -d
```

---

## Production Workflow

### Setup

1. **Set environment variables:**
```bash
# In .env or .env.prod
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_very_secure_password_here
GRAFANA_URL=http://your-domain.com:4000
```

2. **Start with logging:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.logging.prod.yml up -d --build
```

3. **Access Grafana (via Tailscale):**
```bash
# Navigate to http://<tailscale-ip>:4000
```

### Production Configuration

**Log Format:** JSON (structured)
```json
{
  "asctime": "2025-11-20T10:30:45.123Z",
  "name": "apps.blog.views",
  "levelname": "INFO",
  "message": "Post viewed",
  "post_id": 15
}
```

**Retention:**
- Docker logs: 10MB × 3 files = 30MB per container
- Nginx logs: 20MB × 5 files = 100MB
- Loki: 30 days
- Total storage: ~50GB for all services (30 days)

**Services:**
- Django: 30MB (Docker) + ~10GB (Loki)
- Celery Worker: 30MB + ~5GB
- Nginx: 100MB + ~20GB
- Redis: 30MB + ~2GB
- Loki data: ~40GB
- Grafana data: ~500MB

### Monitoring Production

**1. Dashboard Overview:**
- Navigate to Dashboards → "Trung-Dev Application Logs"
- View 4 panels: Django, Errors, Celery, Nginx

**2. Error Alerting (manual check):**
```logql
count_over_time({app="trung-dev", level="ERROR"}[5m])
```

**3. Performance Monitoring:**
```logql
{service="django"} |= "duration_ms" | json | duration_ms > 1000
```

**4. User Activity:**
```logql
{service="django"} |= "Post viewed" | json
```

**5. Celery Task Failures:**
```logql
{service="celery-worker"} |= "failed" | json
```

---

## Configuration Details

### Environment Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| **Log Format** | Verbose (human-readable) | JSON (structured) |
| **Docker Log Size** | 50MB per file | 10MB per file |
| **Docker Log Files** | 5 files | 3 files |
| **Loki Retention** | 7 days | 30 days |
| **Loki Ingestion Rate** | 16MB/s | 32MB/s |
| **Grafana Password** | `admin` (default) | From env var (required) |
| **Restart Policy** | `unless-stopped` | `always` |
| **Total Disk Usage** | ~2GB (1 week) | ~50GB (30 days) |

### Log Rotation Mechanism

**How Docker rotates logs:**

1. Log file grows as container writes to stdout/stderr
2. When file reaches `max-size` (e.g., 10MB):
   - Rename current file to `.log.1`
   - Rotate `.log.1` → `.log.2`, `.log.2` → `.log.3`, etc.
   - Delete oldest file if `max-file` limit reached
   - Create new empty `.log` file

**Example rotation:**
```
Initial state:
  abc123-json.log (8MB)

After reaching 10MB:
  abc123-json.log (0MB, new file)
  abc123-json.log.1 (10MB, old file)

After 2nd rotation:
  abc123-json.log (0MB, newest)
  abc123-json.log.1 (10MB)
  abc123-json.log.2 (10MB, oldest)

After 3rd rotation (max-file=3):
  abc123-json.log (0MB)
  abc123-json.log.1 (10MB)
  abc123-json.log.2 (10MB)
  # .log.3 deleted automatically
```

### Label Strategy

**Container Labels (Docker Compose):**
```yaml
labels: "service=django,environment=production,app=trung-dev"
```

**Promtail Extracted Labels:**
- `container_name`: Docker container name
- `service`: Compose service name
- `environment`: `development` or `production`
- `app`: Application name (`trung-dev`)
- `stream`: `stdout` or `stderr`
- `level`: Log level (INFO, ERROR, etc.) from JSON
- `logger`: Logger name (apps.blog.views) from JSON

**Why labels matter:**
- **Fast queries**: Loki indexes by labels, not content
- **Efficient storage**: Logs with same labels are compressed together
- **Flexible filtering**: Combine labels to narrow down results

---

## Querying Logs

### LogQL Basics

LogQL syntax: `{label="value"} |filter| parser| aggregation`

### Common Queries

**1. View all Django logs:**
```logql
{container_name="django-blog-container"}
```

**2. Filter errors only:**
```logql
{service="django"} |= "ERROR"
```

**3. Parse JSON and filter by field:**
```logql
{service="django"} | json | levelname="ERROR"
```

**4. Search in message:**
```logql
{service="django"} | json | message =~ "Post.*viewed"
```

**5. Exclude patterns:**
```logql
{service="django"} != "healthcheck"
```

**6. Multiple services:**
```logql
{service=~"django|celery-worker"}
```

**7. Time range (last 5 minutes):**
```logql
{service="django"} |= "ERROR" [5m]
```

**8. Count errors per minute:**
```logql
rate({service="django"} |= "ERROR" [1m])
```

**9. View specific user activity:**
```logql
{service="django"} | json | user_id="15"
```

**10. Slow queries (duration > 1 second):**
```logql
{service="django"} | json | duration_ms > 1000
```

### Advanced Queries

**Count logs by log level:**
```logql
sum by (level) (count_over_time({app="trung-dev"} | json [1h]))
```

**Top 10 error messages:**
```logql
topk(10, sum by (message) (count_over_time({service="django"} | json | levelname="ERROR" [24h])))
```

**Celery task success rate:**
```logql
sum(rate({service="celery-worker"} |= "succeeded" [5m])) 
/ 
sum(rate({service="celery-worker"} |~ "succeeded|failed" [5m]))
```

---

## Troubleshooting

### Grafana Not Accessible

**Symptom:** Cannot reach `http://localhost:4000`

**Solutions:**
```bash
# 1. Check if Grafana is running
docker compose ps grafana

# 2. View Grafana logs
docker compose logs -f grafana

# 3. Verify port not in use
lsof -i :4000

# 4. Restart Grafana
docker compose restart grafana

# 5. Check network
docker network inspect simple-django-blog_trungdev-network
```

### No Logs Appearing in Grafana

**Symptom:** Queries return empty results

**Solutions:**
```bash
# 1. Check Promtail is running
docker compose ps promtail

# 2. View Promtail logs (look for errors)
docker compose logs -f promtail

# 3. Check Loki is receiving logs
curl http://localhost:3100/ready
curl http://localhost:3100/metrics | grep promtail

# 4. Verify Docker containers are running
docker compose ps

# 5. Check container labels
docker inspect django-blog-container | grep -A 10 Labels

# 6. Generate test logs
docker compose logs django | head -10
```

### Loki Returns "Too Many Outstanding Requests"

**Symptom:** Error when querying in Grafana

**Solutions:**
```bash
# 1. Reduce query time range (try last 1 hour instead of 24 hours)

# 2. Add more specific filters
{service="django"} # Instead of {app="trung-dev"}

# 3. Increase Loki limits in loki-config.prod.yaml
limits_config:
  max_query_parallelism: 32  # Default: 14
  max_outstanding_requests_per_tenant: 2048  # Default: 100

# 4. Restart Loki
docker compose restart loki
```

### Disk Space Full

**Symptom:** Docker can't write logs, containers crash

**Solutions:**
```bash
# 1. Check disk usage
df -h
docker system df

# 2. Clean old containers
docker system prune

# 3. Remove old log volumes
docker volume ls | grep loki
docker volume rm simple-django-blog_loki-dev-data

# 4. Adjust retention in loki-config
table_manager:
  retention_period: 168h  # Reduce from 720h to 7 days

# 5. Reduce Docker log file size
# In docker-compose.prod.yml
max-size: "5m"  # Reduce from 10m
max-file: "2"   # Reduce from 3
```

### Promtail Not Discovering Containers

**Symptom:** Promtail logs show no targets found

**Solutions:**
```bash
# 1. Check Docker socket permissions
ls -l /var/run/docker.sock

# 2. Verify Promtail has access to Docker socket
docker compose logs promtail | grep "service discovery"

# 3. Check project name filter
# In promtail-config.yaml, verify:
filters:
  - name: label
    values: ["com.docker.compose.project=simple-django-blog"]

# 4. Verify container labels
docker inspect django-blog-container | grep "com.docker.compose.project"

# 5. Restart Promtail
docker compose restart promtail
```

---

## Best Practices

### 1. Logging in Application Code

**✅ DO:**
```python
import logging

logger = logging.getLogger(__name__)

def upload_file(file, filename):
    logger.info(
        "File upload started",
        extra={
            "filename": filename,
            "size": file.size,
            "user_id": request.user.id
        }
    )
    
    try:
        result = storage.save(filename, file)
        logger.info("File uploaded successfully", extra={"url": result})
    except Exception as e:
        logger.exception(
            "File upload failed",
            extra={"filename": filename, "error": str(e)}
        )
        raise
```

**❌ DON'T:**
```python
# Bad: Using print()
print(f"Uploading file: {filename}")

# Bad: Logging sensitive data
logger.info(f"User password: {password}")  # NEVER!

# Bad: No context
logger.error("Upload failed")  # What file? Which user?

# Bad: Logging in loops
for item in large_list:
    logger.debug(f"Processing {item}")  # Too many logs!
```

### 2. Log Levels

Use appropriate log levels:

- **DEBUG**: Detailed diagnostic info (disabled in production)
  ```python
  logger.debug(f"Query: {sql_query}")
  ```

- **INFO**: General informational messages
  ```python
  logger.info("User logged in", extra={"user_id": 123})
  ```

- **WARNING**: Something unexpected but not critical
  ```python
  logger.warning("API rate limit approaching", extra={"remaining": 10})
  ```

- **ERROR**: Errors that need attention
  ```python
  logger.error("Database connection failed", exc_info=True)
  ```

- **CRITICAL**: Severe errors causing service disruption
  ```python
  logger.critical("Disk space < 1GB", extra={"available": disk_space})
  ```

### 3. Structured Logging

Always use `extra={}` parameter:

```python
# Good: Structured data
logger.info(
    "Post viewed",
    extra={
        "post_id": post.id,
        "post_slug": post.slug,
        "user_id": request.user.id,
        "ip_address": request.META.get("REMOTE_ADDR")
    }
)

# Bad: String concatenation
logger.info(f"Post {post.id} viewed by user {request.user.id}")
```

**Why?** Structured logs are:
- Easier to parse in Loki
- Queryable by field: `| json | post_id="15"`
- More consistent across the codebase

### 4. Security Considerations

**Never log:**
- ❌ Passwords
- ❌ API keys / tokens
- ❌ Credit card numbers
- ❌ Social security numbers
- ❌ Private user data (email, phone, address)

**Sanitize before logging:**
```python
# Good: Sanitized
logger.info(
    "Payment processed",
    extra={
        "user_id": user.id,
        "amount": amount,
        "card_last4": card_number[-4:]  # Only last 4 digits
    }
)

# Bad: Exposing sensitive data
logger.info(f"Processing card: {card_number}")  # NEVER!
```

### 5. Performance Optimization

**Avoid expensive operations in log statements:**

```python
# Bad: Always serializes, even if DEBUG not enabled
logger.debug(f"User data: {serialize_user(user)}")

# Good: Lazy evaluation
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"User data: {serialize_user(user)}")
```

**Use log sampling for high-frequency events:**

```python
import random

# Log only 1% of requests
if random.random() < 0.01:
    logger.info("Request processed", extra={"path": request.path})
```

### 6. Grafana Query Optimization

**Fast queries:**
```logql
# Good: Specific labels
{service="django", container_name="django-blog-container"}

# Good: Time range
{service="django"} [1h]

# Good: Limit results
{service="django"} | limit 100
```

**Slow queries (avoid in production):**
```logql
# Bad: No labels (scans all logs)
{} |= "ERROR"

# Bad: Large time range
{service="django"} [30d]

# Bad: Regex on message content
{service="django"} | message =~ ".*very.*complex.*regex.*"
```

### 7. Retention Strategy

**Development:**
- Short retention (7 days)
- Larger log files (easier debugging)
- More verbose logging (DEBUG level)

**Production:**
- Longer retention (30 days)
- Smaller log files (efficient storage)
- Less verbose (INFO level)
- Archive critical logs to S3/GCS if needed

### 8. Monitoring & Alerting

**Set up alerts for:**
- Error rate spike: `rate({service="django"} |= "ERROR" [5m]) > 10`
- Service down: Check Loki has recent logs
- Disk space: Monitor Loki volume size
- Slow queries: `| json | duration_ms > 5000`

**Create dashboards for:**
- Log volume by service
- Error trends over time
- Top error messages
- User activity patterns

---

## Additional Resources

### Official Documentation
- [Grafana Loki](https://grafana.com/docs/loki/latest/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/configuration/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [python-json-logger](https://github.com/madzak/python-json-logger)

### Internal Documentation
- `docs/usefull-command.md` - Section 8: Logging commands
- `.github/copilot-instructions.md` - Project setup guide

### Support
For issues or questions, check:
1. This documentation
2. Docker logs: `docker compose logs -f <service>`
3. Grafana → Explore → Query logs directly

---

**Version History:**
- v1.0 (2025-11-20): Initial documentation

