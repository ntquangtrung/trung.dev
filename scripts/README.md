# Deployment Scripts

Simple deployment script for the Django application.

## Usage

### In CI/CD (GitHub Actions)

The script runs automatically when you trigger the "Manual Deploy to Ubuntu Server" workflow.

### Manual Deployment on Server

```bash
# SSH into your server
ssh user@your-server

# Navigate to project directory
cd ~/your-deploy-path

# Pull latest changes
git pull origin main

# Run deployment
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## What It Does

1. **Stops containers** - Gracefully shuts down all running containers
2. **Starts containers** - Rebuilds and starts with latest code
3. **Includes logging** - Deploys Loki/Grafana stack automatically
4. **Cleans up** - Removes unused Docker images

## Services Deployed

- Django (Gunicorn)
- Celery Worker
- Celery Beat
- Flower
- Redis
- Nginx (reverse proxy)
- Discord Bot
- **Loki** (log storage)
- **Promtail** (log collector)
- **Grafana** (log visualization at port 4000)

## Troubleshooting

**View logs:**
```bash
docker compose logs -f django
```

**Check status:**
```bash
docker compose ps
```

**Restart a service:**
```bash
docker compose restart django
```

**View Grafana:**
```bash
# Access at: http://your-server-ip:4000
# Login with GRAFANA_ADMIN_PASSWORD from .env
```

## Environment Variables

Make sure these are set in your `.env` file:
- `GRAFANA_ADMIN_PASSWORD` - Required for Grafana access
- `GRAFANA_ADMIN_USER` - Optional (defaults to "admin")
- `GRAFANA_URL` - Optional (defaults to http://localhost:4000)
