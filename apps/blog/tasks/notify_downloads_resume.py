from celery import current_app


@current_app.task(bind=True)
def notify_downloads_resume(self):
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc) from exc
