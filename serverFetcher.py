# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

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
	udp.send("\\status\\players\\".encode("ascii"))
	data = udp.recv(4096).decode("ascii")
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


def mergeMapInfo(serverInfo):
	mapname = serverInfo["mapname"]
	modename = serverInfo["gametype"]
	
	try:
		map = Map.get(Map.name == mapname)
	except Map.DoesNotExist:
		map = Map.create(name = mapname)
	
	try:
		mode = Mode.get(Mode.name == modename)
	except Mode.DoesNotExist:
		mode = Mode.create(name = modename)
	
	try:
		MapMode.get(MapMode.map == map, MapMode.mode == mode)
	except MapMode.DoesNotExist:
		MapMode.create(map = map, mode = mode)
	
	return (map, mode)


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
	
	(map, mode) = mergeMapInfo(serverInfo)
	server.map = map
	server.mode = mode
	
	server.version = (lambda v: v[0] + "." + v[1:])(serverInfo["uver"])
	server.maxplayers = serverInfo["maxplayers"]
	if "hbver" in serverInfo:
		server.hradba = serverInfo["hbver"]
	
	server.save()
	
	mergePlayersInfo(server, serverInfo)


def mergePlayersInfo(server, serverInfo):
	playersCount = 0
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
			playersCount += 1
		except KeyError:
			break
	
	server.numplayers = playersCount
	server.save()


def fetchServer(server):
	try:
		mergeServerInfo(server, getServerInfo(server))
	except Exception:
		return False

