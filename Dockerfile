# syntax=docker/dockerfile:1

FROM python:3.13-slim-bookworm

# Set environment variables
ENV POETRY_VERSION=2.0.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock .

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION" && poetry install --only main --no-root --no-directory

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

RUN poetry install --only main

# Expose port (optional, e.g. for Django default)
EXPOSE 8000

# Grant execute permission to the entrypoint.sh script to ensure it can be run as an executable during container startup
RUN chmod +x /app/entrypoint.sh
