from .base import *

DATABASE_URL = f"postgres://{env.str('POSTGRES_USER', 'postgres')}:{env.str('POSTGRES_PASSWORD', 'postgres')}@{env.str('POSTGRES_HOST', 'localhost')}:{env.str('POSTGRES_PORT', '5432')}/{env.str('POSTGRES_DB', 'postgres')}"

DATABASES["default"] = env.db_url_config(DATABASE_URL)

THIRD_PARTY_APPS = ["django_browser_reload", "debug_toolbar"]

INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS + env.list("DJANGO_ALLOWED_HOSTS", default=["localhost"])

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["http://localhost:8001"]
)

INTERNAL_IPS = INTERNAL_IPS + env.list("DJANGO_INTERNAL_IPS", default=["127.0.0.1"])


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "debug_toolbar.middleware.show_toolbar"
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
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
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        # PostgreSQL logging (uncomment to debug database queries)
        # "django.db.backends": {
        #     "handlers": ["console_debug"],
        #     "level": "DEBUG",  # Logs all SQL queries - useful for debugging N+1 queries
        #     "propagate": False,
        # },
        # Application loggers
        "apps.blog": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "services": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "adapters": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "utilities": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "celery": {
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
