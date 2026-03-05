# syntax=docker/dockerfile:1

FROM python:3.13-slim-bookworm

# Create a non-root user and group with home directory (needed for npm cache)
RUN addgroup --system app && adduser --system --ingroup app --home /home/app app

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
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set work directory before any COPY
WORKDIR /app

# Copy poetry files and install dependencies (separate layer for cache efficiency)
COPY pyproject.toml poetry.lock poetry.toml ./
RUN pip install "poetry==$POETRY_VERSION" \
    && poetry install --only main --no-root --no-directory

# Copy source code
COPY . .

# Bake Tailwind CSS into the image — runs npm directly, no Django settings needed
RUN cd theme/static_src \
    && npm install --no-package-lock \
    && npm run build

# Copy entrypoint script and fix ownership in one layer
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
