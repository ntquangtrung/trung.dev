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

# Change ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

EXPOSE 8000
