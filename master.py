#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import socket
import struct

from init import *
from model import *
import aluigi

def encodeList(servers):
	data = struct.pack("s", servers)
	return aluigi.encodeList("bq98mE", data, len(data))


class MasterService(socketserver.TCPServer):
	allow_reuse_address = True
	
	def __init__(self):
		super().__init__(("", 28900), MasterHandler)


class MasterHandler(socketserver.BaseRequestHandler):

	def handle(self):
		self.request.sendall("\\basic\\\\secure\\".encode("latin1"))
		line1 = self.request.recv(4096).decode("latin1")
		line2 = self.request.recv(4096).decode("latin1")
		
		servers = bytearray()
		for server in Server.select().where(Server.online == True):
			servers.extend(socket.inet_aton(server.ip))
			servers.extend(struct.pack("h", server.infoport))
		
		self.request.send(encodeList(servers))


if __name__ == "__main__":
	server = MasterService()
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()

