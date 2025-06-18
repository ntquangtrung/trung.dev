from .base import *
import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(env.db("DATABASE_URL", default="postgres://"))
}

SECRET_KEY = env.str("SECET_KEY", default="your-secret-key")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ALLOWED_HOSTS + ["*", "localhost", "127.0.0.1"]
