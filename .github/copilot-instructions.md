# Copilot Instructions for trung-dev

## Project Overview
Django 5.2+ personal portfolio site with Tailwind CSS 4.x, containerized with Docker. Uses **Poetry** for dependency management (not pip directly). CI/CD via GitHub Actions.

## Architecture & Key Components

### Project Structure
- **Apps:** `apps/blog/` contains all main features (posts, resume, user models)
- **Config:** `config/settings/{base,development,production}.py` for environment-specific settings
- **Admin:** Custom admin classes in `apps/blog/model_admin/*.py` registered in `apps/blog/admin.py`
- **Models:** Split across `apps/blog/models/*.py` with `__init__.py` exporting all models
- **Services:** External integrations abstracted in `services/` (SeaweedFS, Redis, GitHub)
- **Adapters:** API clients in `adapters/` (e.g., `github_adapter.py`)
- **Utilities:** Reusable helpers in `utilities/` (e.g., `VariableResolver` for template variable substitution)

### Storage Architecture
- **Custom Storage Backend:** `apps.blog.storage.SeaweedStorage` implements Django's Storage API for SeaweedFS
- **SeaweedFS Client:** `services/seaweedfs.SeaweedFSClient` provides REST API wrapper
- **Configuration:** Set `SEAWEEDFS_URL` and `SEAWEEDFS_PREFIX` in settings; used in `STORAGES['default']`
- Files are uploaded with prefix: `{SEAWEEDFS_PREFIX}/{filename}`

### Async Tasks
- **Celery + Redis:** Background tasks configured in `config/celery.py`
- **Task Location:** `apps/blog/tasks/` (e.g., `notify_downloads_resume.py`)
- **Broker:** Redis with separate DB indices for broker (`CELERY_BROKER_REDIS_DB_INDEX`) and backend (`CELERY_BACKEND_REDIS_DB_INDEX`)
- **Beat Scheduler:** Uses `django_celery_beat` for periodic tasks stored in database

## Developer Workflows

### Running Commands (Poetry-based)
```bash
# Django commands - ALWAYS use poetry run
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver

# Celery worker
poetry run celery -A config worker --loglevel=info

# Celery beat scheduler
poetry run celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Docker Development
```bash
# Start all services (Django, Tailwind, Redis, Postgres, Celery)
docker-compose up

# Production build (uses docker-compose.prod.yml overlay)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

### Tailwind CSS
- **Source:** `theme/static_src/src/styles.css`
- **Output:** `theme/static/css/dist/styles.css`
- **Build:** `cd theme/static_src && npm run build` (production)
- **Watch:** `cd theme/static_src && npm run dev` (development)
- **Django Integration:** Use `python manage.py tailwind start` for hot reload

### Static Files
```bash
# Collect static files (run after Tailwind build)
poetry run python manage.py collectstatic --noinput
```

### Code Quality
```bash
# Lint and format (REQUIRED before commit)
ruff check .
ruff format .

# Auto-fix issues
ruff check --fix .
```

### CI/CD
- **CI:** `.github/workflows/ci.yml` runs on push/PR - linting, migrations, static collection, Docker build
- **Deploy:** `.github/workflows/deploy.yml` manual trigger for production deployment
- **Tests:** CI runs `poetry run python manage.py test apps` (excludes `/tests` folder)

## Conventions & Patterns

### Admin Registration Pattern
- Admin classes defined in `apps/blog/model_admin/*.py` (e.g., `PostAdmin`, `ResumeAdmin`)
- Import and register in `apps/blog/admin.py`: `admin.site.register(Model, AdminClass)`
- Use `form = CustomForm` for admin form customization
- Split fieldsets for organization (Basic Info, SEO Settings, Timestamps)

### Model Organization
- Models split by domain: `posts.py`, `resume.py`, `user.py`, `github.py`, `click_log.py`
- All models exported via `models/__init__.py` `__all__` list
- Use `django-model-utils` for common patterns (TimeStampedModel)

### Settings Pattern
- Base settings in `config/settings/base.py`
- Environment variables loaded via `django-environ`: `env = environ.Env()`
- Override in `development.py` or `production.py`
- Import settings: `from django.conf import settings` (NOT `from config.settings`)

### Entrypoint Behavior
- `entrypoint.sh` runs migrations automatically on container start
- Creates superuser if `DJANGO_SUPERUSER_*` env vars are set
- Production: starts Gunicorn (`ENVIRONMENT=production`)
- Development: starts `runserver` on `0.0.0.0:8000`

## Integration Points

### SeaweedFS Storage
- Custom storage backend at `apps.blog.storage.SeaweedStorage`
- Client wrapper: `services.seaweedfs.SeaweedFSClient`
- Upload: POST to `{SEAWEEDFS_URL}/{prefix}/{filename}`
- Retrieve: GET from `{SEAWEEDFS_URL}/{filepath}`
- Delete: DELETE to `{SEAWEEDFS_URL}/{filepath}`

### GitHub API
- Adapter: `adapters/github_adapter.py`
- Service: `services/github_service.py`
- Model: `apps.blog.models.GithubRepository` stores repo metadata

### Variable Resolver Utility
- `utilities.resolve_variables.VariableResolver` replaces `{variable.KEY}` patterns
- Supports nested keys: `{variable.PROFILE.SOCIAL.GITHUB.URL}`
- Case-insensitive lookup dict, case-sensitive pattern matching
- Used for dynamic content substitution

## Common Tasks

### Add New Django App
```bash
poetry run python manage.py startapp <appname> apps/<appname>
# Register in config/settings/base.py LOCAL_APPS
```

### Create Migration
```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

### Add Celery Task
1. Create task in `apps/blog/tasks/<taskname>.py`
2. Use `@shared_task` decorator
3. Task autodiscovered via `config/celery.py`

### Update Requirements
```bash
poetry add <package>
```

## Key Files Reference
- **Entry:** `manage.py`, `entrypoint.sh`
- **Settings:** `config/settings/base.py`, `pyproject.toml`
- **Models:** `apps/blog/models/__init__.py`
- **Admin:** `apps/blog/admin.py`, `apps/blog/model_admin/*.py`
- **Storage:** `apps/blog/storage.py`, `services/seaweedfs.py`
- **Async:** `config/celery.py`, `apps/blog/tasks/`
- **CI/CD:** `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- **Docker:** `Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`

---
**Note:** This project uses Poetry exclusively - always prefix Python/Django commands with `poetry run`. Never use `pip install` directly.
