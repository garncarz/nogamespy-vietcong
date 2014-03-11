#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import re
import pygeoip

from model import *

udpTimeout = 4
geoip = pygeoip.GeoIP("/usr/share/GeoIP/GeoIP.dat")


def getServerInfo(server):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.settimeout(udpTimeout)
	udp.connect((server.ip, server.infoport))
	udp.send("\\status\\players\\".encode("latin1"))
	data = udp.recv(4096).decode("latin1")
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


def mergeServerInfo(server, serverInfo):
	server.online = True
	server.offlineSince = None

	server.port = int(serverInfo["hostport"])
	server.password = "password" in serverInfo
	server.dedic = "dedic" in serverInfo
	server.vietnam = "vietnam" in serverInfo
	
	server.country = geoip.country_code_by_addr(server.ip)
	server.countryname = geoip.country_name_by_addr(server.ip)
	
	server.name = serverInfo["hostname"]
	server.mode = serverInfo["gametype"]
	server.mapname = serverInfo["mapname"]
	server.version = (lambda v: v[0] + "." + v[1:])(serverInfo["uver"])
	server.maxplayers = serverInfo["maxplayers"]
	if "hbver" in serverInfo:
		server.hradba = serverInfo["hbver"]
	
	server.save()
	for i in range(int(serverInfo["numplayers"])):
		try:
			playerName = serverInfo["player_" + str(i)]
			try:
				player = Player.get((Player.server == server) &
					(Player.name == playerName) & (Player.online == False))
			except Player.DoesNotExist:
				player = Player(name = playerName, server = server)
			player.online = True
			player.ping = int(serverInfo["ping_" + str(i)])
			player.frags = int(serverInfo["frags_" + str(i)])
			player.save()
		except KeyError:
			break
	
	server.numplayers = server.players.count()
	server.save()


def fetchServer(server):
	try:
		mergeServerInfo(server, getServerInfo(server))
	except ConnectionError:
		pass
	except socket.timeout:
		pass

