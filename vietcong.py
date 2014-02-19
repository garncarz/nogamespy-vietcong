#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from lxml import etree
import socket
import re
from peewee import *
from datetime import datetime
import configparser

iniFile = "vietcong.ini"
udpTimeout = 4

################################################################################
## DATA RETRIEVAL:

def getServersListFile():
	return urlopen("http://gstadmin.gamespy.net/masterserver/" + \
		"?gamename=vietcong&fields=\\hbver\\password\\country\\uver" + \
		"\\hostname\\mapname\\gametype\\numplayers\\maxplayers")

def parseServersList(file):
	tree = etree.parse(file, parser = etree.HTMLParser())
	rows = tree.xpath("/html/body/form/table/tr")[1:]
	
	columns = {
		"ip": 0,
		"infoport": 1,
		"name": 10,
		"mapname": 11,
		"password": 7,
		"country": 8,
		"version": 9,
		"mode": 12,
		"numplayers": 13,
		"maxplayers": 14,
		"hradba": 6 }

	servers = []
	for row in rows:
		server = {}
		for column, order in columns.items():
			value = row[order].text
			if value and value.isdigit(): value = int(value)
			server[column] = value
		server["version"] = (lambda v: v[0] + "." + v[1:]) \
			(str(server["version"]))
		server["country"] = server["country"].lower()
		servers.append(server)
	
	return servers


def getServerInfo(server):
	udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp.settimeout(udpTimeout)
	udp.connect((server["ip"], server["infoport"]))
	udp.send("\\status\\players\\".encode("latin1"))
	return udp.recv(4096).decode("latin1")

def parseServerInfo(data):
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


def mergeServerInfo(server, serverInfo):
	server["port"] = int(serverInfo["hostport"])
	server["password"] = "password" in serverInfo
	server["dedic"] = "dedic" in serverInfo
	server["vietnam"] = "vietnam" in serverInfo
	
	players = []
	for i in range(int(serverInfo["numplayers"])):
		try:
			player = {}
			player["name"] = serverInfo["player_" + str(i)]
			player["ping"] = int(serverInfo["ping_" + str(i)])
			player["frags"] = int(serverInfo["frags_" + str(i)])
			players.append(player)
		except KeyError:
			break
	server["players"] = players
	server["numplayers"] = len(players)


def getAll():
	servers = parseServersList(getServersListFile())
	for server in servers:
		try:
			mergeServerInfo(server, parseServerInfo(getServerInfo(server)))
		except Exception:
			server["error"] = True
	return list(filter(lambda s: not "error" in s, servers))


################################################################################
## LOCAL DATABASE:

config = configparser.ConfigParser()
config.read(iniFile)
db = MySQLDatabase("vietcong", **config["db"])
db.connect()

class BaseModel(Model):
	class Meta:
		database = db

class Server(BaseModel):
	ip = CharField()
	port = IntegerField()
	
	name = CharField()
	mapname = CharField()
	mode = CharField()
	country = CharField(null = True)
	
	version = CharField()
	hradba = CharField(null = True)
	numplayers = IntegerField()
	maxplayers = IntegerField()
	
	password = BooleanField(null = True)
	dedic = BooleanField(null = True)
	vietnam = BooleanField(null = True)
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)


class Player(BaseModel):
	name = CharField()
	ping = IntegerField()
	frags = IntegerField()
	
	server = ForeignKeyField(Server, related_name = "players",
		on_update = "cascade", on_delete = "cascade")
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)

Server.create_table(True)
Player.create_table(True)


def saveServers(servers):
	db.set_autocommit(False)
	Server.update(online = False).execute()
	Player.update(online = False).execute()
	
	for server in servers:
		try:
			serverDb = Server.get((Server.ip == server["ip"]) &
				(Server.port == server["port"]))
			serverDb.online = True
			serverDb.mapname = server["mapname"]
			serverDb.mode = server["mode"]
			serverDb.numplayers = server["numplayers"]
			serverDb.maxplayers = server["maxplayers"]
			serverDb.password = server["password"]
			serverDb.vietnam = server["vietnam"]
		except Server.DoesNotExist:
			serverDb = Server(**server)
		serverDb.save()
		if "players" in server:
			for player in server["players"]:
				try:
					playerDb = Player.get((Player.server == serverDb) &
						(Player.name == player["name"]) &
						(Player.online == False))
					playerDb.online = True
					playerDb.frags = player["frags"]
					playerDb.ping = player["ping"]
				except Player.DoesNotExist:
					playerDb = Player(server = serverDb, **player)
				playerDb.save()
	
	Server.delete().where(Server.online == False).execute()
	Player.delete().where(Player.online == False).execute()
	db.commit()


################################################################################
## RUN:

if __name__ == "__main__":
	servers = getAll()
	saveServers(servers)
