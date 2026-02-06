from datetime import timedelta

from celery import current_app

from .notify_downloads_resume import *  # noqa: F403

current_app.conf.beat_schedule = {
    # "<schedule-name>": {
    #     "task": "<app-path-to-task-function>",
    #     "schedule": <schedule>,
    # }
    # "notify-downloads-resume-every-1-minute": {
    #     "task": "apps.blog.tasks.notify_downloads_resume.notify_downloads_resume",
    #     "schedule": timedelta(minutes=1),
    # },
}
