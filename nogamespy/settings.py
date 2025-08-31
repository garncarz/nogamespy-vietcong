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

# Parse foreign master servers from environment variable
FOREIGN_MASTER_SERVERS = []
foreign_servers_env = os.getenv('FOREIGN_MASTER_SERVERS', '').strip()
if foreign_servers_env:
    FOREIGN_MASTER_SERVERS = [ip.strip() for ip in foreign_servers_env.split(',') if ip.strip()]

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
}

# Add tasks for each foreign master server
for i, server_ip in enumerate(FOREIGN_MASTER_SERVERS):
    CELERYBEAT_SCHEDULE[f'pull_master_{i}'] = {
        'task': 'nogamespy.tasks.pull_master',
        'args': [server_ip],
        'schedule': crontab(minute='*/5'),
    }

# If no foreign servers are configured, keep the original behavior (but avoid Qtracker)
if not FOREIGN_MASTER_SERVERS:
    # Note: Qtracker is down, so this task won't pull from there anymore
    CELERYBEAT_SCHEDULE['pull_master'] = {
        'task': 'nogamespy.tasks.pull_master',
        'schedule': crontab(minute='*/5'),
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
            'format': '%(message)s',
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
