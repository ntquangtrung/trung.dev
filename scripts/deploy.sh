#!/bin/bash
set -e

# =============================================================================
# Production Deployment Script
# =============================================================================
# Stops current containers and starts new ones with latest code.
#
# Usage:
#   ./scripts/deploy.sh
# =============================================================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting deployment...${NC}"

# Compose files
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.logging.yml"

# Stop containers
echo -e "${BLUE}⏹️  Stopping containers...${NC}"
docker compose $COMPOSE_FILES down --remove-orphans

# Start containers
echo -e "${BLUE}▶️  Starting containers...${NC}"
docker compose $COMPOSE_FILES up --build -d

# Clean up old images
echo -e "${BLUE}🧹 Cleaning up...${NC}"
docker image prune -f --filter "dangling=true"

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "View logs: docker compose logs -f django"
echo "Status:    docker compose ps"
