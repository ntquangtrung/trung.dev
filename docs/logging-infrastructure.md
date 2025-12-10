# Logging & Monitoring Infrastructure Documentation

This document explains the centralized logging and monitoring architecture using the Loki-Prometheus-Grafana stack for the `trung-dev` Django project.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Log Flow](#log-flow)
- [Metrics Flow](#metrics-flow)
- [Configuration Files](#configuration-files)
- [Services Monitored](#services-monitored)
- [Grafana Dashboard](#grafana-dashboard)
- [Query Examples](#query-examples)
- [Startup Commands](#startup-commands)
- [Troubleshooting](#troubleshooting)

---

## Overview

The project implements a **modern observability stack** using:

- **Promtail** - Log collector agent (scrapes Docker container logs)
- **Loki** - Log aggregation and storage engine
- **Prometheus** - Metrics collection and time-series database
- **Grafana** - Visualization and dashboards

### Key Benefits

| Feature | Description |
|---------|-------------|
| Centralized Logs | Single source of truth for all container logs |
| Metrics Collection | Application and infrastructure metrics |
| Structured Data | JSON format allows structured querying |
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
                    │  - 10-50MB files       │
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

### Metrics Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION METRICS                           │
├─────────────────────────────────────────────────────────────────┤
│  Django (/metrics endpoint)                                     │
│  - Request counts, latencies                                    │
│  - Custom application metrics                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼────────────────────┐
                    │  Prometheus                    │
                    │  - Scrapes every 30s           │
                    │  - Retention: 15 days          │
                    │  - Query language: PromQL      │
                    └───────────┬────────────────────┘
                                │
                    ┌───────────▼────────────────────┐
                    │  Grafana (Visualization)       │
                    │  - Metrics dashboards          │
                    │  - Alerts (optional)           │
                    └────────────────────────────────┘
```

### Network Architecture

All services run on the `django-blog-app-network` Docker network:

```
┌──────────────────────────────────────────────────────────────────────┐
│                    django-blog-app-network                            │
│                                                                       │
│  ┌─────────┐    ┌──────────┐    ┌───────┐    ┌────────────┐          │
│  │ Django  │───►│ Promtail │───►│ Loki  │◄───│  Grafana   │          │
│  │ Nginx   │    │          │    │ :3100 │    │   :3000    │          │
│  │ Celery  │    │          │    │       │    │            │          │
│  └─────────┘    └──────────┘    └───────┘    └────────────┘          │
│       │                                             ▲                 │
│       │              ┌────────────┐                 │                 │
│       └─────────────►│ Prometheus │─────────────────┘                 │
│     (metrics)        │   :9090    │                                   │
│                      └────────────┘                                   │
│                                                                       │
│  Exposed Ports:                                                       │
│    - Grafana:    localhost:4000                                       │
│    - Loki:       localhost:3100                                       │
│    - Prometheus: localhost:9090                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Promtail

**Image**: `grafana/promtail:3.2.1`
**Container**: `django-promtail-container`

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

**Configuration Highlights**:
- Batch size: 1MB
- Batch wait: 1s
- Docker refresh interval: 15s
- Log level: warn

### 2. Loki

**Image**: `grafana/loki:latest`
**Container**: `django-loki-container`

**Purpose**: Central log aggregation and storage engine

**Key Configuration**:
| Setting | Value | Description |
|---------|-------|-------------|
| HTTP Port | 3100 | API endpoint |
| gRPC Port | 9096 | Internal communication |
| Storage | Filesystem | `/loki/chunks` |
| Retention | 14 days | 336 hours |
| Compression | Snappy | Efficient storage |
| Schema | TSDB v13 | Time-series database |
| Cache | 100MB | Embedded query cache |

**Limits**:
- Ingestion rate: 10 MB/s
- Burst size: 20 MB
- Max streams per user: 10,000
- Max entries per query: 5,000

### 3. Prometheus

**Image**: `prom/prometheus:latest`
**Container**: `django-prometheus-container`

**Purpose**: Metrics collection and time-series storage

**Key Configuration**:
| Setting | Value | Description |
|---------|-------|-------------|
| HTTP Port | 9090 | Web UI and API |
| Scrape Interval | 30s | How often to collect metrics |
| Scrape Timeout | 10s | Timeout per target |
| Retention | 15 days | Storage retention |
| Lifecycle API | Enabled | Runtime config reload |

**Scrape Targets**:
| Job | Target | Description |
|-----|--------|-------------|
| `prometheus` | localhost:9090 | Self-monitoring |
| `django` | django:8000 | Django app metrics |

**Optional Targets** (commented out in config):
- Nginx exporter (9113)
- Redis exporter (9121)
- PostgreSQL exporter (9187)

### 4. Grafana

**Image**: `grafana/grafana:12.3`
**Container**: `django-grafana-container`

**Purpose**: Visualization and dashboarding

**Access**:
```
URL: http://localhost:4000
Credentials: From environment (GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD)
```

**Environment Variables**:
| Variable | Default | Description |
|----------|---------|-------------|
| `GF_SECURITY_ADMIN_USER` | admin | Admin username |
| `GF_SECURITY_ADMIN_PASSWORD` | changeme | Admin password |
| `GF_SERVER_ROOT_URL` | http://localhost:4000 | Public URL |
| `GF_USERS_ALLOW_SIGN_UP` | false | Disable self-registration |
| `TZ` | UTC | Timezone |

**Pre-configured Datasources**:
- **Loki** (default) - Log queries
- **Prometheus** - Metric queries

**Health Check**: `wget --spider -q http://localhost:3000/api/health`

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
│ Flower Filtering             │
│ - Drop Periodic messages     │
│ - Drop inspect messages      │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Celery Filtering             │
│ - Drop heartbeat pings       │
│ - Drop Scheduler messages    │
│ - Drop DatabaseScheduler     │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Django Filtering             │
│ - Drop GET /metrics          │  ← Prometheus scrapes
│ - Drop Gunicorn boot logs    │
│ - Keep custom app logs       │
└──────────────────────────────┘
       │
       ▼
   Clean Logs → Loki
```

---

## Metrics Flow

### Django → Prometheus Journey

1. **Django exposes** `/metrics` endpoint
2. **Prometheus scrapes** every 30 seconds
3. **Prometheus stores** time-series data
4. **Grafana queries** via PromQL

### Available Metrics

Django metrics at `/metrics` may include:
- HTTP request counts by method, path, status
- Request latencies (histograms)
- Active connections
- Custom application metrics

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
├── prometheus/
│   └── prometheus.yml            # Prometheus configuration
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml   # Auto-provision Loki + Prometheus
        └── dashboards/
            ├── dashboards.yml    # Dashboard provisioning config
            └── django-logs.json  # Pre-built dashboard
```

### docker-compose.logging.yml

Defines four services:

```yaml
services:
  loki:
    image: grafana/loki:latest
    container_name: django-loki-container
    ports: ["3100:3100"]
    volumes:
      - ./loki/loki-config.yml:/etc/loki/config.yml:ro
      - loki-data:/loki

  promtail:
    image: grafana/promtail:3.2.1
    container_name: django-promtail-container
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/config.yml:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - promtail-data:/promtail

  prometheus:
    image: prom/prometheus:latest
    container_name: django-prometheus-container
    ports: ["9090:9090"]
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:12.3
    container_name: django-grafana-container
    ports: ["4000:3000"]
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro

volumes:
  loki-data:
  promtail-data:
  prometheus-data:
  grafana-storage:
```

---

## Services Monitored

### Logs (via Promtail → Loki)

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

### Metrics (via Prometheus)

| Service | Target | Metrics Path |
|---------|--------|--------------|
| Django | django:8000 | /metrics |
| Prometheus | localhost:9090 | /metrics |

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

## Query Examples

### LogQL (Loki)

#### Basic Queries

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

#### Filtering by Content

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

#### Aggregations

```logql
# Error rate per minute
rate({app="trung-dev"} |= "ERROR" [1m])

# Log count by service
sum by (service) (count_over_time({app="trung-dev"} [5m]))

# Total logs in time range
count_over_time({app="trung-dev"} [$__range])
```

#### Nginx-Specific

```logql
# All nginx access logs
{service="blog-nginx"}

# 5xx errors
{service="blog-nginx"} |~ "\" 5[0-9]{2} "

# Specific endpoint
{service="blog-nginx"} |= "POST /api"
```

### PromQL (Prometheus)

#### Basic Queries

```promql
# All Django metrics
{job="django"}

# HTTP request rate
rate(django_http_requests_total[5m])

# Request latency (95th percentile)
histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m]))
```

#### Prometheus Self-Monitoring

```promql
# Scrape duration
prometheus_target_scrape_pool_sync_total

# Targets up/down
up{job="django"}
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
docker compose -f docker-compose.yml \
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
| Prometheus | http://localhost:9090 |

---

## Troubleshooting

### Check Service Status

```bash
# View all logging services
docker compose -f docker-compose.logging.yml ps

# Check individual service logs
docker compose logs -f loki
docker compose logs -f promtail
docker compose logs -f prometheus
docker compose logs -f grafana
```

### Verify Loki Health

```bash
# Check readiness
curl http://localhost:3100/ready

# Check metrics
curl http://localhost:3100/metrics
```

### Verify Prometheus Health

```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# Check config
curl http://localhost:9090/api/v1/status/config
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

#### Prometheus can't scrape Django

1. Check Django exposes `/metrics` endpoint
2. Verify network connectivity: `docker exec prometheus wget -qO- http://django:8000/metrics`
3. Check targets in Prometheus UI: http://localhost:9090/targets

#### Dashboard not loading

1. Check Grafana health: `curl http://localhost:4000/api/health`
2. Verify provisioning files exist in `grafana/provisioning/`
3. Check Grafana logs: `docker compose logs grafana`

### Reset Data

```bash
# Remove all log/metric data (start fresh)
docker volume rm django-blog-app-network_loki-data
docker volume rm django-blog-app-network_promtail-data
docker volume rm django-blog-app-network_prometheus-data
docker volume rm django-blog-app-network_grafana-storage

# Restart logging stack
docker compose -f docker-compose.logging.yml up -d
```

---

## Retention Policy

| Component | Retention | Description |
|-----------|-----------|-------------|
| Loki | 14 days | Log data |
| Prometheus | 15 days | Metric data |
| Docker Logs (Loki) | 50MB x 5 | Container log rotation |
| Docker Logs (Promtail) | 10MB x 3 | Container log rotation |
| Docker Logs (Prometheus) | 50MB x 5 | Container log rotation |
| Docker Logs (Grafana) | 50MB x 5 | Container log rotation |

**Automatic Cleanup**:
- Loki compactor runs every 10 minutes
- Retention enforced with 2-hour deletion delay
- Docker log rotation handled by Docker daemon

---

## Environment Variables

### Required for Grafana

| Variable | Description |
|----------|-------------|
| `GRAFANA_ADMIN_USER` | Admin username |
| `GRAFANA_ADMIN_PASSWORD` | Admin password |
| `GRAFANA_ROOT_URL` | Public URL (optional) |
| `TZ` | Timezone (optional, default: UTC) |

These should be set in `.env.prod` or passed via environment.

---

## References

- [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Promtail Configuration](https://grafana.com/docs/loki/latest/clients/promtail/configuration/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
