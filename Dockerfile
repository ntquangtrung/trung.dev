# syntax=docker/dockerfile:1

FROM python:3.13-slim-bookworm

# Create a non-root user and group
RUN addgroup --system app && adduser --system --ingroup app app

# Build-related envs
ENV POETRY_VERSION=2.0.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_MAJOR=22

# Install system dependencies and Node.js, WeasyPrint build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    ca-certificates \
    ibpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Copy poetry files
COPY pyproject.toml poetry.lock poetry.toml ./

# Install Poetry + main dependencies
RUN pip install "poetry==$POETRY_VERSION" \
    && poetry install --only main --no-root --no-directory

# Set work directory and copy source code
WORKDIR /app
COPY . /app

# Copy entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Runtime ARGs (won't affect cached Poetry install)
ARG DJANGO_SETTINGS_MODULE
ARG DEBUG
ARG DJANGO_ALLOWED_HOSTS
ARG DJANGO_CSRF_TRUSTED_ORIGINS
ARG DJANGO_INTERNAL_IPS
ARG GITHUB_PERSONAL_ACCESS_TOKEN
ARG GITHUB_BASE_URL
ARG GITHUB_API_VERSION
ARG REDIS_PASSWORD
ARG REDIS_HOST
ARG REDIS_PORT
ARG REDIS_DB_INDEX
ARG CELERY_BROKER_REDIS_DB_INDEX
ARG CELERY_BACKEND_REDIS_DB_INDEX
ARG FLOWER_USER
ARG FLOWER_PASSWORD
ARG SEAWEEDFS_URL

# Environment variables from ARGs
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
    DEBUG=${DEBUG} \
    DJANGO_INTERNAL_IPS=${DJANGO_INTERNAL_IPS} \
    DJANGO_CSRF_TRUSTED_ORIGINS=${DJANGO_CSRF_TRUSTED_ORIGINS} \
    DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} \
    GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_PERSONAL_ACCESS_TOKEN} \
    GITHUB_BASE_URL=${GITHUB_BASE_URL} \
    GITHUB_API_VERSION=${GITHUB_API_VERSION} \
    REDIS_PASSWORD=${REDIS_PASSWORD} \
    REDIS_HOST=${REDIS_HOST} \
    REDIS_PORT=${REDIS_PORT} \
    REDIS_DB_INDEX=${REDIS_DB_INDEX} \
    CELERY_BROKER_REDIS_DB_INDEX=${CELERY_BROKER_REDIS_DB_INDEX} \
    CELERY_BACKEND_REDIS_DB_INDEX=${CELERY_BACKEND_REDIS_DB_INDEX} \
    FLOWER_USER=${FLOWER_USER} \
    FLOWER_PASSWORD=${FLOWER_PASSWORD} \
    SEAWEEDFS_URL=${SEAWEEDFS_URL}

# Build Tailwind & collect static
RUN SECRET_KEY=dummy poetry run python manage.py tailwind install --no-package-lock --no-input \
    && SECRET_KEY=dummy poetry run python manage.py tailwind build --no-input \
    && SECRET_KEY=dummy poetry run python manage.py collectstatic --no-input

# Change ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000
