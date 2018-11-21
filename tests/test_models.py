from datetime import datetime, timedelta

from sqlalchemy import inspect

from nogamespy.database import db_session
from nogamespy import models, settings

import factories


def test_server_player_relations():
    player1 = factories.Player()
    player2 = factories.Player()
    server = factories.Server(players=[player1, player2])

    db_session.add(server)
    db_session.commit()

    assert player1.server == server
    assert player2.server == server
    assert set(server.players) == set([player1, player2])


def test_map_modes():
    map_ = factories.Map()
    mode1 = factories.Mode(maps=[map_])
    mode2 = factories.Mode(maps=[map_])

    db_session.add_all([mode1, mode2])
    db_session.commit()

    assert map_.modes == [mode1, mode2]


def test_mode_maps():
    mode = factories.Mode()
    map1 = factories.Map(modes=[mode])
    map2 = factories.Map(modes=[mode])

    db_session.add_all([map1, map2])
    db_session.commit()

    assert mode.maps == [map1, map2]


def test_server_map_mode_servers():
    map_ = factories.Map()
    mode = factories.Mode(maps=[map_])

    server1 = factories.Server(map=map_, mode=mode)
    server2 = factories.Server(map=map_, mode=mode)

    db_session.add_all([server2, server2])
    db_session.commit()

    assert server1.map_id == map_.id
    assert server1.mode_id == mode.id

    assert map_.modes == [mode]
    assert map_.servers == [server1, server2]

    assert mode.maps == [map_]
    assert mode.servers == [server1, server2]


def test_remove_offline_entities():
    server1 = factories.Server(online=False, offline_since=datetime.now() - timedelta(minutes=5))
    server2 = factories.Server(online=False, offline_since=datetime.now() - timedelta(minutes=20))
    server3 = factories.Server(online=True, offline_since=datetime.now() - timedelta(hours=2))
    # meaning it went offline 2 hours ago, but is online again, thus it should not be deleted

    player1 = factories.Player(server=server1, online=True)  # by mistake still set to be online
    player2 = factories.Player(server=server2)
    player3 = factories.Player(server=server3, online=True)
    player4 = factories.Player(server=server3, online=False)

    db_session.add_all([server1, server2, server3])
    db_session.commit()

    settings.KEEP_OFFLINE_SERVERS_FOR_MINUTES = 10
    models.remove_offline_entities()

    assert not inspect(server1).was_deleted
    assert inspect(server2).was_deleted
    assert not inspect(server3).was_deleted

    assert server3.offline_since is None

    assert inspect(player1).was_deleted
    assert inspect(player2).was_deleted
    assert not inspect(player3).was_deleted
    assert inspect(player4).was_deleted

    settings.KEEP_OFFLINE_SERVERS_FOR_MINUTES = 0
    models.remove_offline_entities()

    assert inspect(server1).was_deleted
    assert not inspect(server3).was_deleted
    assert not inspect(player3).was_deleted


def test_set_server_offline_since():
    server = factories.Server(online=False)

    db_session.add(server)
    db_session.commit()

    models.remove_offline_entities()

    assert datetime.now() - server.offline_since < timedelta(seconds=10)  # "now", but test can run slowly
