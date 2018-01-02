import logging
import socket
import socketserver
import struct

import aluigi
from . import models, settings


logger = logging.getLogger(__name__)


def _encode_list(servers):
    return aluigi.encodeList('bq98mE', memoryview(servers).tobytes())


class MasterService(socketserver.TCPServer):

    allow_reuse_address = True

    def __init__(self):
        super().__init__(('', settings.MASTER_PORT), MasterHandler)


class MasterHandler(socketserver.BaseRequestHandler):

    def handle(self):
        logger.debug(f'Responding to {self.request.getpeername()[0]}...')

        self.request.sendall('\\basic\\\\secure\\'.encode('latin1'))

        # TODO cache for some small amount of time
        servers = bytearray()

        for server in models.Server.query.filter_by(online=True).all():
            servers.extend(socket.inet_aton(server.ip))
            servers.extend(struct.pack('>h', server.info_port))

        servers.extend(b'\\final\\')

        self.request.send(_encode_list(servers))