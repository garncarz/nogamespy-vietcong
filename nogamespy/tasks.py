import logging
import socket

from celery import group, chord
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

    group(register.s(ip, port) for ip, port in servers)()

    statsd.increment('foreign_master_pulled')


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
    
    # Report player count as a gauge metric with server tags
    statsd.gauge('game_server.players', players_count, tags=[
        f'ip:{server.ip}',
        f'name:{server.name}' if server.name else 'name:unknown'
    ])


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


@task
def pull_server_info(server):
    if isinstance(server, int):
        server = models.Server.query.get(server)

    assert isinstance(server, models.Server)

    logger.debug(f'Pulling info for {server}...')

    try:
        info = protocol.get_server_info(server)

        db_session.add(server)
        _merge_server_info(server, info)
        server.waiting_for_sync = False
        db_session.commit()  # so players can attach to server.id

        _merge_players_info(server, info)
        db_session.commit()

        logger.debug(f'Pulled info for {server}')
        statsd.increment('game_server.pulled', tags=[f'ip:{server.ip}'])
        return True

    except socket.timeout:
        logger.debug(f'{server}: UDP timeout')
        statsd.increment('game_server.connection_error', tags=[f'ip:{server.ip}', 'error:timeout'])
        return False

    except ConnectionRefusedError:
        logger.debug(f'{server}: connection refused')
        statsd.increment('game_server.connection_error', tags=[f'ip:{server.ip}', 'error:connection_refused'])
        return False

    except OSError as e:
        if e.errno == 113:  # no route to host
            logger.debug(f'{server}: no route to host')
            statsd.increment('game_server.connection_error', tags=[f'ip:{server.ip}', 'error:no_route_to_host'])
            return False
        raise

    except KeyError:
        logger.exception(f'{server}: key error')
        statsd.increment('game_server.key_error', tags=[f'ip:{server.ip}'])
        return False

    except pygeoip.GeoIPError:
        logger.exception(f'{server}: GeoIP error')
        statsd.increment('game_server.geoip_error', tags=[f'ip:{server.ip}'])
        return False


@task
def refresh_all_servers():
    logger.debug(f'Refreshing info for all saved servers...')

    models.Server.query.update({'waiting_for_sync': True})
    models.Player.query.update({'online': False})
    db_session.commit()

    chord(
        (pull_server_info.s(server.id) for server in models.Server.query.all()),
        after_all_servers_are_refreshed.s()
    )()


@task
def after_all_servers_are_refreshed(_results):
    models.Server.query.filter_by(waiting_for_sync=True).update({'online': False})
    models.remove_offline_entities()

    # Report total number of online players across all servers
    total_online_players = db_session.query(models.Player).filter_by(online=True).count()
    statsd.gauge('game_servers.total_players', total_online_players)
    
    # Report total number of online servers
    total_online_servers = db_session.query(models.Server).filter_by(online=True).count()
    statsd.gauge('game_servers.total_servers', total_online_servers)

    statsd.increment('servers_refreshed')


@task
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

            if models.delete_if_persistent(server):
                db_session.commit()

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
