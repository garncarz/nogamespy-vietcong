from datadog import DogStatsd

from . import settings

statsd = DogStatsd(
    host=settings.STATSD_HOST,
    port=settings.STATSD_PORT,
    namespace=settings.STATSD_PREFIX,
)
