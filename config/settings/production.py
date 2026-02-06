from .base import *

DATABASE_URL = f"postgres://{env.str('POSTGRES_USER', 'postgres')}:{env.str('POSTGRES_PASSWORD', 'postgres')}@{env.str('POSTGRES_HOST', 'localhost')}:{env.str('POSTGRES_PORT', '5432')}/{env.str('POSTGRES_DB', 'postgres')}"

THIRD_PARTY_APPS = ["django_prometheus"]

INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    *MIDDLEWARE,
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

DATABASES["default"] = env.db_url_config(DATABASE_URL)

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

DEBUG = False

# ALLOWED_HOSTS configuration:
# - "django": Internal Docker network (for Prometheus scraping)
# - "localhost", "127.0.0.1": For local testing in production mode
# - Add your domain via DJANGO_ALLOWED_HOSTS env variable
ALLOWED_HOSTS = ALLOWED_HOSTS + env.list("DJANGO_ALLOWED_HOSTS", default=[]) + [
    "django",      # Internal Docker network hostname (Prometheus, internal services)
    "localhost",   # Local testing
    "127.0.0.1",   # Local testing
]

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Standardized logging configuration for production
# All logs output as JSON to stdout for collection by Promtail -> Loki -> Grafana
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d %(funcName)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        # Django core loggers
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",  # Changed from ERROR to INFO to capture all requests
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # PostgreSQL logging (commented out - uncomment to enable)
        # Option 1: ERROR - Only log database connection/query errors
        # "django.db.backends": {
        #     "handlers": ["console"],
        #     "level": "ERROR",
        #     "propagate": False,
        # },
        # Option 2: DEBUG - Log ALL SQL queries (verbose, use for debugging slow queries)
        # "django.db.backends": {
        #     "handlers": ["console"],
        #     "level": "DEBUG",
        #     "propagate": False,
        # },
        # Application loggers
        "apps.blog": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "services": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "adapters": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "utilities": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Celery logging
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.task": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.worker": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
