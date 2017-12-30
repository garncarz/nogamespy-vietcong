import logging
import re
import socket

import pygeoip
import requests

from . import models, settings
from .database import db_session

logger = logging.getLogger(__name__)

geoip = pygeoip.GeoIP('/usr/share/GeoIP/GeoIP.dat')


def _get_qtracker_list():
    resp = requests.get('http://www.qtracker.com/server_list_details.php?game=vietcong')
    for line in resp.text.splitlines():
        ip, port = line.split(':')
        yield ip, port


def pull_master():
    for ip, port in _get_qtracker_list():
        server, created = models.get_or_create(models.Server, ip=ip, info_port=port)

        if created:
            logger.info(f'New server: {server}')
            pull_server_info(server)


def _get_server_info(server):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(settings.UDP_TIMEOUT)
    udp.connect((server.ip, int(server.info_port)))

    udp.send('\\status\\players\\'.encode('ascii'))
    data = udp.recv(4096).decode('ascii')
    arr = re.split('\\\\', data)[1:-4]

    return dict(zip(arr[::2], arr[1::2]))


def _get_map_and_mode(info):
    map_name = info['mapname']
    mode_name = info['gametype']

    map_, _ = models.get_or_create(models.Map, name=map_name)
    mode, _ = models.get_or_create(models.Mode, name=mode_name)

    models.get_or_create(models.MapMode, map=map_name, mode=mode_name)

    return map_, mode


def _merge_players_info(server, info):
    players_count = 0

    for i in range(int(info['numplayers'])):
        try:
            player_name = info['player_' + str(i)]
            player = models.get_or_create(models.Player, server=server, name=player_name, online=False)

            player.online = True
            player.ping = int(info['ping_' + str(i)])
            player.frags = int(info['frags_' + str(i)])

            db_session.add(player)

            players_count += 1
        except KeyError:
            break

    server.num_players = players_count


def _merge_server_info(server, info):
    server.online = True
    server.offline_since = None

    server.port = int(info['hostport'])
    server.password = 'password' in info
    server.dedicated = 'dedic' in info
    server.vietnam = 'vietnam' in info

    server.country = geoip.country_code_by_addr(server.ip)
    server.country_name = geoip.country_name_by_addr(server.ip)

    server.name = info['hostname']

    map_, mode = _get_map_and_mode(info)
    server.map = map_.name
    server.mode = mode.name

    server.version = (lambda v: v[0] + '.' + v[1:])(info['uver'])
    server.max_players = info['maxplayers']
    if 'hbver' in info:
        server.hradba = info['hbver']

    _merge_players_info(server, info)


def pull_server_info(server):
    if isinstance(server, int):
        server = models.Server.query.get(server)

    assert isinstance(server, models.Server)

    info = _get_server_info(server)

    db_session.add(server)
    _merge_server_info(server, info)

    db_session.commit()
