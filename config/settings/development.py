from .base import *


DEBUG = True

DATABASES["default"] = env.db(
    "DATABASE_URL", default="postgres://postgres:postgres@localhost:5432/postgres"
)
