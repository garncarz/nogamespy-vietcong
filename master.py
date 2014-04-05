#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import socket
import struct

from init import *
from model import *

class MasterService(socketserver.TCPServer):
	allow_reuse_address = True
	
	def __init__(self):
		super().__init__(("", 28900), MasterHandler)


class MasterHandler(socketserver.BaseRequestHandler):

	def handle(self):
		self.request.sendall("\\basic\\\\secure\\".encode("latin1"))
		line1 = self.request.recv(4096).decode("latin1")
		line2 = self.request.recv(4096).decode("latin1")
		
		for server in Server.select().where(Server.online == True):
			ip = socket.inet_aton(server.ip)
			port = struct.pack("h", server.infoport)
			self.request.send(ip)
			self.request.send(port)


if __name__ == "__main__":
	server = MasterService()
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()

