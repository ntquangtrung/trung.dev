from .base import *
import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(env.db("DATABASE_URL", default="postgres://"))
}

SECRET_KEY = env.str("SECET_KEY", default="your-secret-key")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ALLOWED_HOSTS + env.list("DJANGO_ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
