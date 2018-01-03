import socket
import time
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
    time.sleep(0.1)

    resp = client.recv(4096)
    assert resp == b"\\basic\\\\secure\\\xe4bq98mE\x00\x00\xac~\xcd#]k\xc3'\xdeI[\xa4t\xc40\r\xf0v\xda\x86\x06^0\xdc"

    client.close()

    master_server.shutdown()
    master_server.server_close()
    master_thread.join()


def test_decode_list():
    encrypted = b"\xe4bq98mE\x00\x00\xac~\xcd#]k\xc3'\xdeI[\xa4t\xc40\r\xf0v\xda\x86\x06^0\xdc"
    assert list(protocol.decode_list(encrypted)) == [
        ('1.2.3.4', 15425),
        ('5.6.7.10', 15426),
    ]
