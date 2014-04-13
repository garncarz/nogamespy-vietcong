#!/usr/bin/python

# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

import socketserver

import crawler


class HeartbeatService(socketserver.UDPServer):
	allow_reuse_address = True
	
	def __init__(self):
		super().__init__(("", 27900), HeartbeatHandler)


class HeartbeatHandler(socketserver.BaseRequestHandler):

	def handle(self):
		msg = self.request[0].decode("ascii").split("\\")
		if msg[1] != "heartbeat":
			return
		crawler.register(ip = self.client_address[0], port = msg[2])



if __name__ == "__main__":
	server = HeartbeatService()
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()

