from nogamespy.database import db_session

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


def test_server_mode():
    mode = factories.Mode()
    db_session.add(mode)
    db_session.commit()

    server = factories.Server(mode=mode.name)

    db_session.add(server)
    db_session.commit()

    assert server.mode == mode.name
