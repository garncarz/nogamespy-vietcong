import socket
import threading

from nogamespy import protocol, settings
from nogamespy.database import db_session

import factories


def test_master_server():
    server1 = factories.Server(ip='1.2.3.4', info_port=15425, online=True)
    server2 = factories.Server(ip='5.6.7.10', info_port=15426, online=True)
    server3 = factories.Server(ip='10.9.8.7', info_port=15425, online=False)
    db_session.add_all([server1, server2, server3])
    db_session.commit()

    master_server = protocol.MasterService()
    master_thread = threading.Thread(target=master_server.serve_forever)
    master_thread.start()

    client = socket.create_connection(('127.0.0.1', settings.MASTER_PORT))

    client.send(b'pls')

    resp = client.recv(4096).decode('latin1')
    assert resp  # TODO be more precise

    client.close()

    master_server.shutdown()
    master_server.server_close()
    master_thread.join()
