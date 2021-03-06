from datetime import timedelta
import logging.config
import os

from celery.schedules import crontab

DATABASE = os.getenv('DATABASE', 'postgresql://postgres@db/postgres')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis')

GAMESPY_KEY = 'bq98mE'

UDP_TIMEOUT = 4

MASTER_PORT = 28900
HEARTBEAT_PORT = 27900

KEEP_OFFLINE_SERVERS_FOR_MINUTES = 30

# Celery:
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_EXPIRES = timedelta(minutes=10)
CELERYD_HIJACK_ROOT_LOGGER = False

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

SENTRY_DSN = os.getenv('SENTRY_DSN')

LOGZIO_TOKEN = os.getenv('LOGZIO_TOKEN')
LOGZIO_LEVEL = os.getenv('LOGZIO_LEVEL', 'INFO')

STATSD_HOST = os.getenv('STATSD_HOST', 'localhost')
STATSD_PORT = int(os.getenv('STATSD_PORT', '8125'))
STATSD_PREFIX = 'nogamespy'


def sentry_filter(record):
    if (record.name.startswith('celery.')
            and record.levelno < logging.WARNING):
        return False

    return True


LOGGING = lambda: {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
        },
        'logzioFormat': {
            'format': '{"app": "nogamespy"}',
        },
    },

    'filters': {
        'mute_at_sentry': {
            '()': lambda: sentry_filter,
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
            'filters': ['mute_at_sentry'],
            # 'release': raven.fetch_git_sha(BASE_DIR),
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


try:
    from .settings_local import *
except ImportError:
    pass


LOGGING = LOGGING()

if LOGZIO_TOKEN:
    LOGGING['handlers']['logzio'] = {
        'level': LOGZIO_LEVEL,
        'class': 'logzio.handler.LogzioHandler',
        'formatter': 'logzioFormat',
        'token': LOGZIO_TOKEN,
        'logzio_type': 'python',
        'logs_drain_timeout': 5,
        'url': 'https://listener.logz.io:8071',
        'debug': False,
    }

    LOGGING['loggers']['']['handlers'].append('logzio')

logging.config.dictConfig(LOGGING)
