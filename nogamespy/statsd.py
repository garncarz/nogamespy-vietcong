from statsd import StatsClient

from . import settings

statsd = StatsClient(
    host=settings.STATSD_HOST,
    port=settings.STATSD_PORT,
    prefix=settings.STATSD_PREFIX,
)
