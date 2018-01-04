import logging
import socket
import socketserver
import struct

import aluigi
from . import models, tasks, settings


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

        tasks.register(ip=self.client_address[0], port=msg[2])
