from celery import current_app

current_app.conf.beat_schedule = {
    # "<schedule-name>": {
    #     "task": "<app-path-to-task-function>",
    #     "schedule": <schedule>,
    # }
}
