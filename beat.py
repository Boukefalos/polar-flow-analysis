from tasks import celery
from datetime import timedelta

class Config:
    CELERYBEAT_SCHEDULE = {
        'add-every-x-seconds': {
            'task': 'tasks.add',
            'schedule': timedelta(seconds=1),
            'args': (1, 2)
        },
    }
    CELERY_TIMEZONE = 'Europe/London'

celery.config_from_object(Config)