import logging
import socket

import pygeoip
import requests
import sqlalchemy

from . import celery, models, protocol
from .database import db_session
from .statsd import statsd

logger = logging.getLogger(__name__)

task = celery.app.task

geoip = pygeoip.GeoIP('/usr/share/GeoIP/GeoIP.dat')


def _get_qtracker_list():
    logger.debug('Fetching new servers from Qtracker...')

    resp = requests.get('http://www.qtracker.com/server_list_details.php?game=vietcong')
    for line in resp.text.splitlines():
        ip, port = line.split(':')
        yield ip, port


@task
def pull_master(source=None):
    servers = _get_qtracker_list() if not source else protocol.fetch_from_master(source)

    for ip, port in servers:
        register(ip, port)

    statsd.incr('foreign_master_pulled')


def _get_map_and_mode(info):
    map_name = info['mapname']
    mode_name = info['gametype']

    map_, _ = models.get_or_create(models.Map, name=map_name)
    mode, _ = models.get_or_create(models.Mode, name=mode_name)

    if mode not in map_.modes:
        map_.modes.append(mode)
        db_session.add(map_)

    return map_, mode


def _merge_players_info(server, info):
    players_count = 0

    for i in range(int(info['numplayers'])):
        try:
            player_name = info['player_' + str(i)]
            player, _ = models.get_or_create(models.Player, server=server, name=player_name, online=False)

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
    server.map = map_
    server.mode = mode

    server.version = (lambda v: v[0] + '.' + v[1:])(info['uver'])
    server.max_players = info['maxplayers']
    if 'hbver' in info:
        server.hradba = info['hbver']


def pull_server_info(server):
    if isinstance(server, int):
        server = models.Server.query.get(server)

    assert isinstance(server, models.Server)

    logger.debug(f'Pulling info for {server}...')

    try:
        info = protocol.get_server_info(server)

        db_session.add(server)
        _merge_server_info(server, info)
        db_session.commit()  # so players can attach to server.id

        _merge_players_info(server, info)
        db_session.commit()

        logger.debug(f'Pulled info for {server}')
        return True

    except socket.timeout:
        logger.debug(f'{server}: UDP timeout')
        return False

    except ConnectionRefusedError:
        logger.debug(f'{server}: connection refused')
        return False


@task
def refresh_all_servers():
    logger.debug(f'Refreshing info for all saved servers...')

    models.Server.query.update({'online': False})
    models.Player.query.update({'online': False})
    db_session.commit()

    for server in models.Server.query.all():
        pull_server_info(server)

    models.remove_offline_entities()

    statsd.incr('servers_refreshed')


def register(ip, port, print_it=False, force_pull=False):
    logger.debug(f'Trying to register {ip}:{port}...')

    server, created = models.get_or_create(models.Server, ip=ip, info_port=port)

    if not created and not force_pull:
        if print_it:
            print('EXISTS')
        return True

    else:
        if pull_server_info(server):
            logger.info(f'New server: {server}')
            if print_it:
                print('OK')
            return True

        else:
            if print_it:
                print('FAIL')

            try:
                db_session.delete(server)
                db_session.commit()
            except sqlalchemy.exc.InvalidRequestError:
                # SQLite does "Instance '<Server at ...>' is not persisted"
                # TODO check it, it seems the row exists in DB
                logger.exception('Could not delete server.')

            return False


def run_master_server():
    logger.info('Running master server...')
    server = protocol.MasterService()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


def run_heartbeat_server():
    logger.info('Running heartbeat server...')
    server = protocol.HeartbeatService()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
