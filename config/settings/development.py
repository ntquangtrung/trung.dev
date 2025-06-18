from .base import *


DATABASES["default"] = env.db(
    "DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/postgres"
)

THIRD_PARTY_APPS = ["django_browser_reload"]

INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

DEBUG = env.bool("DEBUG", default=True)
