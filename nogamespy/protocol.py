import logging
import re
import socket
import socketserver
import struct

import aluigi
from . import models, tasks, settings
from .statsd import statsd


logger = logging.getLogger(__name__)


def encode_list(decrypted):
    return aluigi.encode_list(settings.GAMESPY_KEY, memoryview(decrypted).tobytes())


def decode_list(encrypted):
    decrypted = aluigi.decode_list(settings.GAMESPY_KEY, encrypted)

    for i in range(0, len(decrypted) - 1, 6):
        if decrypted[i:].startswith(b'\\final'):
            break

        ip = socket.inet_ntoa(decrypted[i:i+4])
        port = struct.unpack('>h', decrypted[i+4:i+6])[0]
        yield ip, port


class MasterService(socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self):
        super().__init__(('', settings.MASTER_PORT), MasterHandler)


class MasterHandler(socketserver.BaseRequestHandler):

    def handle(self):
        logger.debug(f'Responding to {self.request.getpeername()[0]}...')

        self.request.sendall('\\basic\\\\secure\\'.encode('latin1'))

        # TODO cache for some small amount of time
        byte_string = bytearray()

        for server in models.Server.query.filter_by(online=True).all():
            # TODO move byte schema to encode_list
            byte_string.extend(socket.inet_aton(server.ip))
            byte_string.extend(struct.pack('>h', server.info_port))

        byte_string.extend(b'\\final\\')

        self.request.send(encode_list(byte_string))

        statsd.incr('master_pulled')


class HeartbeatService(socketserver.UDPServer):

    allow_reuse_address = True

    def __init__(self):
        super().__init__(('', settings.HEARTBEAT_PORT), HeartbeatHandler)


class HeartbeatHandler(socketserver.BaseRequestHandler):

    def handle(self):
        logger.debug(f'Got heartbeat from {self.client_address[0]}...')

        msg = self.request[0].decode('ascii').split('\\')

        if msg[1] != 'heartbeat':
            return

        tasks.register(ip=self.client_address[0], port=msg[2], force_pull=True)

        statsd.incr('heartbeat_registered')


def fetch_from_master(ip):
    logger.debug(f'Fetching new servers from {ip}...')

    client = socket.create_connection((ip, settings.MASTER_PORT))

    client.recv(4096)

    client.send(b'\\gamename\\vietcong\\gamever\\2\\location\\0\\validate\\JOzySo8c\\enctype\\2\\final\\'
                b'\\queryid\\1.1\\\\list\\cmp\\gamename\\vietcong\\final\\')

    resp = client.recv(4096)
    servers = decode_list(resp)

    client.close()

    return servers


def get_server_info(server):
    logger.debug(f'Trying to get info from {server.ip}:{server.info_port}...')

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(settings.UDP_TIMEOUT)
    udp.connect((server.ip, int(server.info_port)))

    udp.send('\\status\\players\\'.encode('ascii'))
    data = udp.recv(4096).decode('ascii')
    arr = re.split('\\\\', data)[1:-4]

    return dict(zip(arr[::2], arr[1::2]))
