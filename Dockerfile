# syntax=docker/dockerfile:1

FROM python:3.13-slim-bookworm

# Create a non-root user and group
RUN addgroup --system app && \
    adduser --system --ingroup app app

ARG DJANGO_SETTINGS_MODULE
ARG DEBUG
ARG DJANGO_ALLOWED_HOSTS
ARG DJANGO_CSRF_TRUSTED_ORIGINS
ARG DJANGO_INTERNAL_IPS
ARG SUPABASE_S3_REGION
ARG SUPABASE_S3_ACCESS_KEY
ARG SUPABASE_S3_SECRET_ACCESS_KEY
ARG SUPABASE_STORAGE_BUCKET_NAME
ARG SUPABASE_PROJECT_REF
ARG GITHUB_PERSONAL_ACCESS_TOKEN
ARG GITHUB_BASE_URL
ARG GITHUB_API_VERSION

# Set environment variables
ENV POETRY_VERSION=2.0.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_MAJOR=22 \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
    DEBUG=${DEBUG} \
    DJANGO_INTERNAL_IPS=${DJANGO_INTERNAL_IPS} \
    DJANGO_CSRF_TRUSTED_ORIGINS=${DJANGO_CSRF_TRUSTED_ORIGINS} \
    DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} \
    SUPABASE_S3_REGION=${SUPABASE_S3_REGION} \
    SUPABASE_S3_ACCESS_KEY=${SUPABASE_S3_ACCESS_KEY} \
    SUPABASE_S3_SECRET_ACCESS_KEY=${SUPABASE_S3_SECRET_ACCESS_KEY} \
    SUPABASE_STORAGE_BUCKET_NAME=${SUPABASE_STORAGE_BUCKET_NAME} \
    SUPABASE_PROJECT_REF=${SUPABASE_PROJECT_REF} \
    SUPABASE_S3_ENDPOINT_URL=https://${SUPABASE_PROJECT_REF}.supabase.co/storage/v1/s3 \
    SUPABASE_CUSTOM_DOMAIN=${SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/${SUPABASE_STORAGE_BUCKET_NAME} \
    GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_PERSONAL_ACCESS_TOKEN} \
    GITHUB_BASE_URL=${GITHUB_BASE_URL} \
    GITHUB_API_VERSION=${GITHUB_API_VERSION}



# Install system dependencies and Node.js, WeasyPrint build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    ca-certificates \
    # WeasyPrint dependencies (non-wheel build)
    ibpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    # Node.js install prep
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Copy poetry files
COPY pyproject.toml poetry.lock poetry.toml .

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION" && poetry install --only main --no-root --no-directory

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Ensure entrypoint.sh was placed outside of /app directory, else "chmod +x /usr/local/bin/entrypoint.sh" will not work
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
# Grant execute permission to the entrypoint.sh script to ensure it can be run as an executable during container startup
RUN chmod +x /usr/local/bin/entrypoint.sh

# Run Tailwind install + build + collectstatic (must set dummy SECRET_KEY)
RUN SECRET_KEY=dummy poetry run python manage.py tailwind install --no-package-lock --no-input
RUN SECRET_KEY=dummy poetry run python manage.py tailwind build --no-input
RUN SECRET_KEY=dummy poetry run python manage.py collectstatic --no-input

# Give ownership of the app directory to the new user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Expose port (optional, e.g. for Django default)
EXPOSE 8000
