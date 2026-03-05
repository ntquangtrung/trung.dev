# GitHub Actions Workflows Documentation

This document explains the CI/CD pipeline structure and workflows for the `trung-dev` Django project.

## Table of Contents

- [Overview](#overview)
- [Workflow Architecture](#workflow-architecture)
- [Individual Workflows](#individual-workflows)
- [Reusable Components](#reusable-components)
---

## Overview

The project uses a modular GitHub Actions pipeline with:

- **Reusable workflows** for composability
- **Sequential orchestration** for safe deployments
- **SSH-based deployment** for secure server access

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
              │        DEPLOY.YML             │
              │  • Connect via SSH            │
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
3. **Security**: SSH-based deployment
4. **Idempotency**: Deployments can be safely re-run

### Job Dependencies

```yaml
ci → deploy
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
2. `deploy` - Deploys to production server (requires CI success)

**Usage**:

```bash
# Manual trigger via GitHub UI
Actions → Orchestrator - CI, Test, and Deploy → Run workflow
```

**Configuration**:

- Uses `workflow_call` to invoke reusable workflows
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

### 3. deploy.yml

**Purpose**: Deploy application to production server via SSH

**Triggers**:

- Called by orchestrator (`workflow_call`)
- Manual trigger (`workflow_dispatch`)

**Environment**: `production`

**Steps**:

1. **Checkout Repo**: Get latest code
2. **Setup SSH**: Configure SSH access to server
3. **Deploy via SSH**: Execute deployment on server

**Deployment Process**:

```bash
# 1. Clone or update repository
git clone/pull from GitHub (using PAT token)

# 2. Write .env file with environment variables

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
- Redis (cache)
- Nginx (reverse proxy)
- Logging stack (Loki, Promtail, Grafana)

---

## Architecture Decisions

### Why Separate Workflows?

- **Modularity**: Run stages independently
- **Debugging**: Easier to identify failure points
- **Reusability**: Each workflow can be called elsewhere
- **Clear separation**: CI vs Deployment

### Why Manual Orchestrator Trigger?

- **Control**: Deployments are intentional, not accidental
- **Safety**: Prevents unintended production changes
- **CI on PRs**: Code quality checked on pull requests automatically

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
