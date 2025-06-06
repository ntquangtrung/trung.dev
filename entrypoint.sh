#!/bin/sh

poetry run python manage.py makemigrations --settings=config.settings.development
poetry run python manage.py migrate --settings=config.settings.development
poetry run python manage.py runserver 0.0.0.0:8000 --settings=config.settings.development
