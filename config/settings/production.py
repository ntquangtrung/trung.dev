from .base import *

DATABASE_URL = f"postgres://{env.str('POSTGRES_USER', 'postgres')}:{env.str('POSTGRES_PASSWORD', 'postgres')}@{env.str('POSTGRES_HOST', 'localhost')}:{env.str('POSTGRES_PORT', '5432')}/{env.str('POSTGRES_DB', 'postgres')}"

DATABASES["default"] = env.db_url_config(DATABASE_URL)

SECRET_KEY = env.str("SECRET_KEY", default="your-secret-key")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ALLOWED_HOSTS + env.list("DJANGO_ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
