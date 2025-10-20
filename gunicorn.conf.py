"""Gunicorn production configuration for Django Blog"""

import logging
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
graceful_timeout = 30
keepalive = 5

# Worker temp directory (use memory for performance)
worker_tmp_dir = "/dev/shm"

# Logging
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = "info"
capture_output = True

# Process naming
proc_name = "django-blog"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed - usually handled by Nginx)
# keyfile = None
# certfile = None

# Preload app for better performance and memory usage
preload_app = True


# Server hooks
def on_starting(_server):
    """Called just before the master process is initialized."""
    logging.info("🚀 Gunicorn master process starting")


def on_reload(_server):
    """Called to recycle workers during a reload via SIGHUP."""
    logging.info("🔄 Gunicorn reloading")


def when_ready(server):
    """Called just after the server is started."""
    logging.info("✅ Gunicorn server is ready. Spawning %d workers", server.cfg.workers)


def pre_fork(_server, _worker):
    """Called just before a worker is forked."""


def post_fork(_server, worker):
    """Called just after a worker has been forked."""
    logging.info("👷 Worker spawned (pid: %d)", worker.pid)


def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    logging.warning("⚠️  Worker %d received SIGINT/SIGQUIT", worker.pid)


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    logging.error("❌ Worker %d received SIGABRT", worker.pid)


def worker_exit(_server, worker):
    """Called when a worker is exiting."""
    logging.info("👋 Worker %d exiting", worker.pid)
