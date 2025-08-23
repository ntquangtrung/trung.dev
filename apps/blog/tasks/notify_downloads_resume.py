from celery import current_app
from services.redis import ResumeCache


@current_app.task(bind=True)
def notify_downloads_resume(self):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)
