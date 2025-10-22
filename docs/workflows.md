# GitHub Actions Workflows Documentation

This document explains the CI/CD pipeline structure and workflows for the `trung-dev` Django project.

## 📋 Table of Contents

- [Overview](#overview)
- [Workflow Architecture](#workflow-architecture)
- [Individual Workflows](#individual-workflows)
- [Reusable Components](#reusable-components)

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
│                   (Main Entry Point)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │         CI.YML                │
              │  • Lint (Ruff)                │
              │  • Test (Django + Services)   │
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
              │  • Docker Compose deploy      │
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
- Manual: `workflow_dispatch`
- Automatic: Push to `master` branch

**Jobs**:
1. `ci` - Runs the full CI pipeline
2. `tailscale-connection` - Verifies server connectivity
3. `deploy` - Deploys to production server

**Usage**:
```bash
# Manual trigger via GitHub UI
Actions → Orchestrator → Run workflow

# Automatic on git push
git push origin master
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
- Direct push to `master` branch
- Pull requests to `master`

**Jobs**:

#### Job: `lint`
Runs code quality checks:
- **Ruff linter**: Syntax and style issues
- **Ruff formatter**: Code formatting validation

**Tools**: Python 3.13, Ruff

#### Job: `test`
Runs Django tests with full service stack:
- **Services**: PostgreSQL 16, Redis 7
- **Tests**: Django test suite
- **Tailwind**: Builds CSS assets
- **Static files**: Collects static files
- **Migrations**: Validates no missing migrations

**Environment Variables**:
```yaml
ENVIRONMENT: development
DJANGO_SETTINGS_MODULE: config.settings.development
POSTGRES_*: Database credentials
REDIS_*: Redis configuration
```

#### Job: `security`
Security vulnerability scanning:
- **Safety**: Checks Python dependencies for known CVEs
- Continues on error (informational)

#### Job: `build`
Docker image build validation:
- **Docker Buildx**: Multi-platform build support
- **GitHub Cache**: Layer caching for faster builds
- **Production config**: Tests production Docker image

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
- ✅ Hostname and OS version
- ✅ Current user
- ✅ System uptime
- ✅ Docker installation and status
- ✅ Docker Compose availability
- ✅ Disk space usage
- ✅ Memory usage

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
2. **Setup Tailscale and SSH**: Uses composite action (no ping)
3. **Deploy via SSH**: Execute deployment script on server

**Deployment Process**:
```bash
# 1. Clone or update repository
git clone/pull from GitHub

# 2. Write .env file with all secrets/variables
cat > .env << EOT
  POSTGRES_DB=...
  DJANGO_SECRET_KEY=...
  # ... all environment variables
EOT

# 3. Deploy with Docker Compose
docker compose down
docker compose -f docker-compose.yml \
               -f docker-compose.prod.yml \
               up --build -d

# 4. Cleanup
docker image prune -f --filter "dangling=true"
```

**Stack Deployed**:
- Django web application
- PostgreSQL database
- Redis (cache + Celery broker)
- Celery worker
- Celery beat scheduler
- Nginx (reverse proxy)

---

## Reusable Components

### Composite Action: setup-tailscale-ssh

**Location**: `.github/actions/setup-tailscale-ssh/action.yml`

**Purpose**: Encapsulate common Tailscale + SSH setup logic

**Inputs**:
| Input | Required | Description |
|-------|----------|-------------|
| `oauth-client-id` | ✅ | Tailscale OAuth client ID |
| `oauth-secret` | ✅ | Tailscale OAuth secret |
| `ssh-private-key` | ✅ | SSH private key for server |
| `server-host` | ✅ | Server hostname (Tailscale IP/hostname) |
| `server-user` | ✅ | SSH username |
| `skip-ping` | ❌ | Skip ping test (default: `false`) |

**Steps Performed**:
1. Setup Tailscale using `tailscale/github-action@v4`
2. Load SSH private key using `webfactory/ssh-agent@v0.9.1`
3. Add server to `~/.ssh/known_hosts`
4. Optionally ping server via Tailscale

**Usage Example**:
```yaml
- name: Setup Tailscale and SSH
  uses: ./.github/actions/setup-tailscale-ssh
  with:
    oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    ssh-private-key: ${{ secrets.SERVER_SSH_KEY }}
    server-host: ${{ vars.SERVER_HOST }}
    server-user: ${{ vars.SERVER_USER }}
    skip-ping: 'false'
```

**Why Composite Action?**
- DRY: Used in both `tailscale-connection` and `deploy` workflows
- Consistency: Same setup logic everywhere
- Maintainability: Update once, applies everywhere
- Flexibility: `skip-ping` parameter for different use cases

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

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Tailscale GitHub Action](https://github.com/tailscale/github-action)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
