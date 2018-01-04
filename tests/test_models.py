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


def test_server_map_mode():
    map_ = factories.Map()
    mode = factories.Mode()
    map_mode = models.MapMode(map=map_, mode=mode)

    server = factories.Server(map=map_, mode=mode)

    db_session.add_all([server, map_mode])
    db_session.commit()

    assert server.map_id == map_.id
    assert server.mode_id == mode.id

    assert map_mode.map_id == map_.id
    assert map_mode.mode_id == mode.id
