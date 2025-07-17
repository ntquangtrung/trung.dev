from .base import *


DATABASES["default"] = env.db(
    "DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/postgres"
)

THIRD_PARTY_APPS = ["django_browser_reload", "debug_toolbar"]

INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ALLOWED_HOSTS + env.list("DJANGO_ALLOWED_HOSTS", default=["localhost"])

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["http://localhost:8001"]
)

INTERNAL_IPS = INTERNAL_IPS + env.list("DJANGO_INTERNAL_IPS", default=["127.0.0.1"])


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "debug_toolbar.middleware.show_toolbar"
}
