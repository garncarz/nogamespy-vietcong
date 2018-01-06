from nogamespy.database import db_session
from nogamespy import models

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
