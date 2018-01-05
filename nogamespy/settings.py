from celery.schedules import crontab

DATABASE = 'sqlite:///volume/db.sqlite'

GAMESPY_KEY = 'bq98mE'

UDP_TIMEOUT = 4

MASTER_PORT = 28900
HEARTBEAT_PORT = 27900

# Celery:
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL = 'redis://redis'

CELERYBEAT_SCHEDULE = {
    'refresh_all_servers': {
        'task': 'nogamespy.tasks.refresh_all_servers',
        'schedule': crontab(minute='*/2'),
    },
    'pull_master': {
        'task': 'nogamespy.tasks.pull_master',
        'schedule': crontab(minute='*/5'),
    },
}

try:
    from .settings_local import *
except ImportError:
    pass
