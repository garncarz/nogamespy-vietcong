import logging

import requests

from . import models

logger = logging.getLogger(__name__)


def get_qtracker_list():
    resp = requests.get('http://www.qtracker.com/server_list_details.php?game=vietcong')
    for line in resp.text.splitlines():
        ip, port = line.split(':')
        yield ip, port


def pull_master():
    for ip, port in get_qtracker_list():
        server, created = models.get_or_create(models.Server, ip=ip, info_port=port)

        if created:
            logger.info(f'New server: {server}')
