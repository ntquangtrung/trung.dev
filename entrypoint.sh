#!/bin/bash
set -euo pipefail

echo "Starting Django application..."

# Collect static files
echo "Collecting static files..."
poetry run python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
poetry run python manage.py migrate --no-input

# Create superuser if env vars are set
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  echo "Creating superuser..."
  poetry run python manage.py createsuperuser --noinput || true
fi

# Detect environment via DJANGO_SETTINGS_MODULE
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
  echo "Starting Gunicorn server..."
  exec poetry run gunicorn config.wsgi:application --config gunicorn.conf.py
else
  echo "Starting Django development server..."
  exec poetry run python manage.py runserver 0.0.0.0:8000
fi
