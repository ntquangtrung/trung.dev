# Logging Infrastructure Documentation

This document explains the centralized logging architecture using the Loki-Grafana stack for the `trung-dev` Django project.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Log Flow](#log-flow)
- [Configuration Files](#configuration-files)
- [Services Monitored](#services-monitored)
- [Grafana Dashboard](#grafana-dashboard)
- [LogQL Query Examples](#logql-query-examples)
- [Startup Commands](#startup-commands)
- [Troubleshooting](#troubleshooting)

---

## Overview

The project implements a **modern centralized logging architecture** using:

- **Promtail** - Log collector agent (scrapes Docker container logs)
- **Loki** - Log aggregation and storage engine
- **Grafana** - Visualization and dashboards

### Key Benefits

| Feature | Description |
|---------|-------------|
| Centralized Logs | Single source of truth for all container logs |
| Structured Data | JSON format allows structured querying in production |
| Noise Reduction | Smart filtering at collection time |
| Fast Search | Label-based indexing with real-time updates |
| 14-Day Retention | Compressed storage with automatic cleanup |

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTAINER LOGS                              │
├──────────────────────┬──────────────────────┬──────────────────┤
│ Django/Gunicorn      │ Celery Workers/Beat  │ Nginx            │
│ (JSON formatted)     │ (JSON formatted)     │ (stdout/stderr)  │
└──────────────────────┴──────────────────────┴──────────────────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Docker JSON Logger    │
                    │  - 10-20MB files       │
                    │  - 3-5 file rotation   │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────────────┐
                    │  Promtail (Docker SD)          │
                    │  - Reads docker.sock           │
                    │  - Filters: app=trung-dev      │
                    │  - Relabels: service, env      │
                    │  - Drops noise: health, static │
                    └───────────┬────────────────────┘
                                │
                    ┌───────────▼────────────────────┐
                    │  Loki (Log Aggregator)         │
                    │  - Stores compressed chunks    │
                    │  - Retention: 14 days          │
                    │  - Query language: LogQL       │
                    └───────────┬────────────────────┘
                                │
                    ┌───────────▼────────────────────┐
                    │  Grafana (Visualization)       │
                    │  - Dashboard: Django Logs      │
                    │  - Real-time: 30s refresh      │
                    └────────────────────────────────┘
```

### Network Architecture

All logging services run on the `django-blog-app-network` Docker network:

```
┌─────────────────────────────────────────────────────────────┐
│                  django-blog-app-network                    │
│                                                             │
│  ┌─────────┐    ┌──────────┐    ┌───────┐    ┌─────────┐  │
│  │ Django  │    │ Promtail │───►│ Loki  │◄───│ Grafana │  │
│  │ Nginx   │    │          │    │ :3100 │    │ :3000   │  │
│  │ Celery  │    │          │    │       │    │         │  │
│  └─────────┘    └──────────┘    └───────┘    └─────────┘  │
│       │              ▲                            │        │
│       │              │                            │        │
│       └──────────────┘                            │        │
│      (via docker.sock)                      :4000 (host)   │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Promtail

**Purpose**: Collects logs from Docker containers and pushes to Loki

**Key Features**:
- Connects via Docker socket for automatic container discovery
- Filters containers by label `app=trung-dev`
- Applies smart noise reduction (health checks, static files, heartbeats)
- Adds consistent labels for querying

**Labels Applied**:
| Label | Example | Description |
|-------|---------|-------------|
| `app` | trung-dev | Application identifier |
| `service` | blog, celery-worker | Service name |
| `environment` | production | Environment type |
| `container` | django-blog-container | Container name |
| `stack` | django-blog | Stack identifier |

### 2. Loki

**Purpose**: Central log aggregation and storage engine

**Key Configuration**:
| Setting | Value | Description |
|---------|-------|-------------|
| HTTP Port | 3100 | API endpoint |
| Storage | Filesystem | `/loki/chunks` |
| Retention | 14 days | 336 hours |
| Compression | Snappy | Efficient storage |
| Schema | TSDB v13 | Time-series database |

### 3. Grafana

**Purpose**: Visualization and dashboarding

**Access**:
```
URL: http://localhost:4000
Credentials: From .env.prod (GF_SECURITY_ADMIN_USER/PASSWORD)
```

**Pre-configured**:
- Loki datasource (auto-provisioned)
- Django Logs dashboard (auto-provisioned)

---

## Log Flow

### Container → Loki Journey

1. **Application writes log** → stdout/stderr
2. **Docker captures** → JSON file (`/var/lib/docker/containers/...`)
3. **Promtail scrapes** → via Docker socket
4. **Promtail filters** → drops noise, adds labels
5. **Promtail pushes** → HTTP POST to Loki
6. **Loki indexes** → by labels (inverted index)
7. **Loki stores** → compressed chunks on filesystem
8. **Grafana queries** → LogQL via Loki API

### Filtering Pipeline (Promtail)

```
Raw Docker Logs
       │
       ▼
┌──────────────────────────────┐
│ Drop non-app containers      │  ← Only app=trung-dev
│ Drop tailwind, redis logs    │  ← Noise reduction
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Nginx Filtering              │
│ - Drop health checks         │
│ - Drop /static/* requests    │
│ - Drop /favicon.ico          │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Celery Filtering             │
│ - Drop heartbeat pings       │
│ - Drop scheduler messages    │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Gunicorn Filtering           │
│ - Drop "Booting worker"      │
│ - Drop "Listening at"        │
│ - Keep custom app logs       │
└──────────────────────────────┘
       │
       ▼
   Clean Logs → Loki
```

---

## Configuration Files

### File Structure

```
project/
├── docker-compose.logging.yml    # Logging stack services
├── loki/
│   └── loki-config.yml           # Loki configuration
├── promtail/
│   └── promtail-config.yml       # Promtail configuration
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml   # Auto-provision Loki datasource
        └── dashboards/
            ├── dashboards.yml    # Dashboard provisioning config
            └── django-logs.json  # Pre-built dashboard
```

### docker-compose.logging.yml

Defines three services:

```yaml
services:
  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]
    volumes:
      - ./loki/loki-config.yml:/etc/loki/config.yml:ro
      - loki-data:/loki

  promtail:
    image: grafana/promtail:3.2.1
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/config.yml:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro

  grafana:
    image: grafana/grafana:12.3.0
    ports: ["4000:3000"]
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
```

---

## Services Monitored

| Service | Label | Logs Collected |
|---------|-------|----------------|
| Django/Gunicorn | `service=blog` | Application logs, request handling |
| Nginx | `service=blog-nginx` | HTTP access/errors (filtered) |
| Celery Worker | `service=celery-worker` | Job execution, failures |
| Celery Beat | `service=celery-beat` | Task scheduling |
| Flower | `service=flower` | Task monitoring |
| Discord Bot | `service=discord-bot` | Bot events |

**Excluded** (noise reduction):
- Tailwind (CSS builder)
- Redis (cache/broker)

---

## Grafana Dashboard

### Pre-configured Panels

1. **Total Log Lines** - Count of all logs in time range
2. **Error Count** - Logs matching `error|exception|critical`
3. **Warning Count** - Logs matching `warning|warn`
4. **Log Volume by Service** - Stacked time series chart
5. **Nginx Access Logs** - Raw access log viewer
6. **Application Logs** - Filterable by service (dropdown)
7. **Errors & Exceptions** - Filtered error log viewer

### Dashboard Features

| Feature | Value |
|---------|-------|
| Auto-refresh | 30 seconds |
| Default time range | Last 1 hour |
| Service filter | Multi-select dropdown |
| Tags | django, logs, loki, nginx |

---

## LogQL Query Examples

### Basic Queries

```logql
# All application logs
{app="trung-dev"}

# Specific service
{service="blog"}
{service="celery-worker"}
{service="blog-nginx"}

# Multiple services
{service=~"blog|celery-worker"}
```

### Filtering by Content

```logql
# Errors only
{app="trung-dev"} |= "ERROR"

# Case-insensitive error search
{app="trung-dev"} |~ "(?i)error|exception|critical"

# Exclude certain patterns
{service="blog"} != "health"

# JSON field extraction (production logs)
{app="trung-dev"} | json | levelname="ERROR"
```

### Aggregations

```logql
# Error rate per minute
rate({app="trung-dev"} |= "ERROR" [1m])

# Log count by service
sum by (service) (count_over_time({app="trung-dev"} [5m]))

# Total logs in time range
count_over_time({app="trung-dev"} [$__range])
```

### Nginx-Specific

```logql
# All nginx access logs
{service="blog-nginx"}

# 5xx errors
{service="blog-nginx"} |~ "\" 5[0-9]{2} "

# Specific endpoint
{service="blog-nginx"} |= "POST /api"
```

---

## Startup Commands

### Development with Logging

```bash
docker compose -f docker-compose.yml \
               -f docker-compose.logging.yml \
               up -d --build
```

### Production with Logging

```bash
docker compose --env-file .env.prod \
               -f docker-compose.yml \
               -f docker-compose.prod.yml \
               -f docker-compose.logging.yml \
               up --build -d
```

### Access Points

| Service | URL |
|---------|-----|
| Application | http://localhost:8001 |
| Grafana | http://localhost:4000 |
| Loki API | http://localhost:3100 |

---

## Troubleshooting

### Check Service Status

```bash
# View all logging services
docker compose -f docker-compose.logging.yml ps

# Check individual service logs
docker compose logs -f loki
docker compose logs -f promtail
docker compose logs -f grafana
```

### Verify Loki Health

```bash
# Check readiness
curl http://localhost:3100/ready

# Check metrics
curl http://localhost:3100/metrics
```

### Common Issues

#### No logs appearing in Grafana

1. Check Promtail is running: `docker compose logs promtail`
2. Verify container labels include `app=trung-dev`
3. Check Loki connection: `curl http://localhost:3100/ready`

#### Promtail can't connect to Loki

1. Verify network: both services on `django-blog-app-network`
2. Check Loki is healthy: `docker compose ps loki`
3. Review Promtail logs for connection errors

#### Dashboard not loading

1. Check Grafana health: `curl http://localhost:4000/api/health`
2. Verify provisioning files exist in `grafana/provisioning/`
3. Check Grafana logs: `docker compose logs grafana`

### Reset Log Data

```bash
# Remove all log data (start fresh)
docker volume rm django-blog-app-network_loki-data
docker volume rm django-blog-app-network_grafana-storage

# Restart logging stack
docker compose -f docker-compose.logging.yml up -d
```

---

## Log Retention Policy

| Environment | Docker Logs | Loki Retention |
|-------------|-------------|----------------|
| Development | 50MB × 5 files | 7 days |
| Production | 10MB × 3 files | 14 days |
| Nginx | 20MB × 5 files | 14 days |

**Automatic Cleanup**:
- Loki compactor runs every 10 minutes
- Retention enforced with 2-hour deletion delay
- Docker log rotation handled by Docker daemon

---

## Django Logging Configuration

### Production (JSON Format)

```python
# config/settings/production.py
LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {"formatter": "json", "class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {"level": "INFO"},
        "apps.blog": {"level": "INFO"},
        "celery": {"level": "INFO"},
    },
}
```

### Development (Human-Readable)

```python
# config/settings/development.py
LOGGING = {
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}"},
    },
    "handlers": {
        "console": {"formatter": "verbose", "class": "logging.StreamHandler"},
    },
    "loggers": {
        "apps.blog": {"level": "DEBUG"},
    },
}
```

---

## References

- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/configuration/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Grafana Dashboard Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
