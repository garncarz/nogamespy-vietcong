from celery import Celery, signals

from . import settings
from .database import db_session


app = Celery('nogamespy', include=['nogamespy.tasks'])

app.config_from_object('nogamespy.settings')

app.conf.result_expires = settings.CELERY_RESULT_EXPIRES


@signals.task_postrun.connect
def task_postrun(**kwargs):
    # releasing the session, so the next task starts from scratch
    db_session.remove()
