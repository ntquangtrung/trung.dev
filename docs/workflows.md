# GitHub Actions Workflows Documentation

This document explains the CI/CD pipeline structure and workflows for the `trung-dev` Django project.

## Table of Contents

- [Overview](#overview)
- [Workflow Architecture](#workflow-architecture)
- [Individual Workflows](#individual-workflows)
- [Reusable Components](#reusable-components)
- [Secrets and Variables](#secrets-and-variables)

---

## Overview

The project uses a modular GitHub Actions pipeline with:
- **Reusable workflows** for composability
- **Composite actions** for DRY setup code
- **Sequential orchestration** for safe deployments
- **Tailscale VPN** for secure server access

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR.YML                        │
│                (Manual Trigger Only)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │         CI.YML                │
              │  • Lint (Ruff)                │
              │  • Test (Build + Migrations)  │
              │  • Security Check (Safety)    │
              │  • Docker Build               │
              └───────────────────────────────┘
                              │
                              ▼ (on success)
              ┌───────────────────────────────┐
              │  TAILSCALE-CONNECTION.YML     │
              │  • Setup Tailscale VPN        │
              │  • Ping server                │
              │  • Test SSH connectivity      │
              │  • Check server status        │
              └───────────────────────────────┘
                              │
                              ▼ (on success)
              ┌───────────────────────────────┐
              │        DEPLOY.YML             │
              │  • Connect via Tailscale      │
              │  • Clone/Pull repository      │
              │  • Update .env file           │
              │  • Run deploy.sh script       │
              └───────────────────────────────┘
```

---

## Workflow Architecture

### Design Principles

1. **Fail Fast**: Each stage must pass before proceeding
2. **Modularity**: Workflows can be run independently or orchestrated
3. **Reusability**: Common setup extracted into composite actions
4. **Security**: Secrets isolated, Tailscale for VPN access
5. **Idempotency**: Deployments can be safely re-run

### Job Dependencies

```yaml
ci → tailscale-connection → deploy
```

Each job uses `needs:` to enforce sequential execution.

---

## Individual Workflows

### 1. orchestrator.yml

**Purpose**: Main entry point that orchestrates the full CI/CD pipeline

**Triggers**:
- Manual only: `workflow_dispatch`

**Jobs**:
1. `ci` - Runs the full CI pipeline
2. `tailscale-connection` - Verifies server connectivity (requires CI success)
3. `deploy` - Deploys to production server (requires tailscale-connection success)

**Usage**:
```bash
# Manual trigger via GitHub UI
Actions → Orchestrator - CI, Test, and Deploy → Run workflow
```

**Configuration**:
- Uses `workflow_call` to invoke reusable workflows
- Passes `secrets: inherit` to child workflows
- Each job depends on previous job's success

---

### 2. ci.yml

**Purpose**: Continuous Integration - validate code quality and build

**Triggers**:
- Called by orchestrator (`workflow_call`)
- Pull requests to `master` branch

**Jobs**:

#### Job: `lint`
Runs code quality checks:
- **Ruff linter**: Syntax and style issues
- **Ruff formatter**: Code formatting validation

**Tools**: Python 3.13, Ruff

#### Job: `test`
Runs Django build and migration checks with full service stack:
- **Services**: PostgreSQL 16, Redis 7
- **Tailwind**: Builds CSS assets via Node.js 22
- **Migrations**: Runs and validates no missing migrations
- **Static files**: Collects static files

**Package Manager**: Poetry (not pip)

**Environment Variables**:
```yaml
ENVIRONMENT: development
DJANGO_SETTINGS_MODULE: config.settings.development
POSTGRES_*: Database credentials
REDIS_*: Redis configuration
SEAWEEDFS_URL: SeaweedFS storage URL
```

**System Dependencies Installed**:
- libpq-dev, python3-dev, build-essential
- Cairo/Pango libraries (for PDF generation)
- libffi-dev, shared-mime-info

#### Job: `security`
Security vulnerability scanning:
- **Safety**: Checks Python dependencies for known CVEs
- Continues on error (informational)

#### Job: `build`
Docker image build validation:
- **Docker Buildx**: Multi-platform build support
- **GitHub Cache**: Layer caching for faster builds
- **Production config**: Tests production Docker image with build args

**Dependencies**: Requires `lint` and `test` to pass

---

### 3. tailscale-connection.yml

**Purpose**: Verify server connectivity before deployment

**Triggers**:
- Called by orchestrator (`workflow_call`)
- Manual trigger (`workflow_dispatch`)

**Environment**: `production` (requires approval if configured)

**Steps**:

1. **Checkout Code**: Required to access composite action
2. **Setup Tailscale and SSH**: Uses composite action with ping enabled
3. **Test SSH Connection**: Comprehensive server health check

**Server Health Check Reports**:
- Hostname and OS version
- Current user and kernel version
- System uptime
- Docker installation and status
- Docker Compose availability
- Disk space usage
- Memory usage

**Why This Exists**:
- Validates Tailscale VPN is operational
- Confirms SSH access before deployment
- Provides server status snapshot
- Fails early if infrastructure issues exist

---

### 4. deploy.yml

**Purpose**: Deploy application to production server via SSH

**Triggers**:
- Called by orchestrator (`workflow_call`)
- Manual trigger (`workflow_dispatch`)

**Environment**: `production`

**Steps**:

1. **Checkout Repo**: Get latest code
2. **Setup Tailscale and SSH**: Uses composite action (ping skipped)
3. **Deploy via SSH**: Execute deployment on server

**Deployment Process**:
```bash
# 1. Clone or update repository
git clone/pull from GitHub (using PAT token)

# 2. Write .env file with all secrets/variables
# (see Secrets and Variables section)

# 3. Run deployment script
bash scripts/deploy.sh
```

**Deploy Script (`scripts/deploy.sh`)**:
```bash
# Compose files used
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.logging.yml"

# Stop containers
docker compose $COMPOSE_FILES down --remove-orphans

# Start containers
docker compose $COMPOSE_FILES up --build -d

# Cleanup
docker image prune -f --filter "dangling=true"
```

**Stack Deployed**:
- Django web application
- PostgreSQL database
- Redis (cache + Celery broker)
- Celery worker
- Celery beat scheduler
- Nginx (reverse proxy)
- Flower (Celery monitoring)
- Logging stack (Loki, Promtail, Grafana)

---

## Reusable Components

### Composite Action: setup-tailscale-ssh

**Location**: `.github/actions/setup-tailscale-ssh/action.yml`

**Purpose**: Encapsulate common Tailscale + SSH setup logic

**Inputs**:
| Input | Required | Description |
|-------|----------|-------------|
| `oauth-client-id` | Yes | Tailscale OAuth client ID |
| `oauth-secret` | Yes | Tailscale OAuth secret |
| `ssh-private-key` | Yes | SSH private key for server |
| `server-host` | Yes | Server hostname (Tailscale IP/hostname) |
| `server-user` | Yes | SSH username |
| `skip-ping` | No | Skip ping test (default: `false`) |

**Steps Performed**:
1. Setup Tailscale using `tailscale/github-action@v4` with tag `tag:ci`
2. Load SSH private key using `webfactory/ssh-agent@v0.9.1`
3. Add server to `~/.ssh/known_hosts` via ssh-keyscan
4. Optionally ping server via Tailscale (3 attempts)

**Usage Example**:
```yaml
- name: Setup Tailscale and SSH
  uses: ./.github/actions/setup-tailscale-ssh
  with:
    oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    ssh-private-key: ${{ secrets.SERVER_SSH_KEY }}
    server-host: ${{ secrets.SERVER_HOST }}
    server-user: ${{ secrets.SERVER_USER }}
    skip-ping: 'false'
```

---

## Secrets and Variables

### Required Secrets

| Secret | Description |
|--------|-------------|
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID |
| `TS_OAUTH_SECRET` | Tailscale OAuth secret |
| `SERVER_SSH_KEY` | SSH private key for server |
| `SERVER_HOST` | Server hostname (Tailscale IP) |
| `SERVER_USER` | SSH username |
| `DEPLOY_PAT_TOKEN` | GitHub PAT for cloning private repo |
| `POSTGRES_USER` | Database username |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Database host |
| `POSTGRES_PORT` | Database port |
| `POSTGRES_DB` | Database name |
| `DJANGO_SECRET_KEY` | Django secret key |
| `CLIENT_GITHUB_TOKEN` | GitHub API token for client |
| `CLIENT_GITHUB_BASE_URL` | GitHub API base URL |
| `CLIENT_GITHUB_API_VERSION` | GitHub API version |
| `REDIS_PASSWORD` | Redis password |
| `FLOWER_PASSWORD` | Flower dashboard password |
| `SEAWEEDFS_URL` | SeaweedFS storage URL |
| `GRAFANA_ADMIN_USER` | Grafana admin username |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password |

### Required Variables

| Variable | Description |
|----------|-------------|
| `DEPLOY_PATH` | Server path for deployment |
| `ENVIRONMENT` | Environment name (e.g., `production`) |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts for Django |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | CSRF trusted origins |
| `REDIS_HOST` | Redis hostname |
| `REDIS_PORT` | Redis port |
| `REDIS_DB_INDEX` | Redis database index |
| `CELERY_BROKER_REDIS_DB_INDEX` | Celery broker Redis DB |
| `CELERY_BACKEND_REDIS_DB_INDEX` | Celery backend Redis DB |
| `FLOWER_USER` | Flower dashboard username |

---

## Architecture Decisions

### Why Tailscale?

- **Security**: No exposed ports, VPN-only access
- **Simplicity**: No bastion hosts or VPN config
- **Cost**: Free for small teams
- **Reliability**: Mesh network, automatic failover

### Why Separate Workflows?

- **Modularity**: Run stages independently
- **Debugging**: Easier to identify failure points
- **Reusability**: Each workflow can be called elsewhere
- **Clear separation**: CI vs Infrastructure vs Deployment

### Why Composite Actions?

- **DRY principle**: Don't repeat Tailscale/SSH setup
- **Maintainability**: Update once, applies everywhere
- **Testability**: Can be tested independently
- **Flexibility**: Parameters allow customization

### Why Manual Orchestrator Trigger?

- **Control**: Deployments are intentional, not accidental
- **Safety**: Prevents unintended production changes
- **CI on PRs**: Code quality checked on pull requests automatically

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Tailscale GitHub Action](https://github.com/tailscale/github-action)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
