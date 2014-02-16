#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from lxml import etree
import socket
import re
from peewee import *
import configparser

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
		servers.append(server)
	
	return servers


def getServerInfo(server):
	conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	conn.settimeout(2)
	conn.connect((server["ip"], server["infoport"]))
	conn.send("\\status\\players\\".encode("latin1"))
	return conn.recv(4096).decode("latin1")

def parseServerInfo(data):
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


def mergeServerInfo(server, serverInfo):
	server["port"] = int(serverInfo["hostport"])
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


def getAll():
	servers = parseServersList(getServersListFile())
	for server in servers:
		try:
			mergeServerInfo(server, parseServerInfo(getServerInfo(server)))
		except Exception:
			servers.remove(server)
	return servers


################################################################################
## LOCAL DATABASE:

config = configparser.ConfigParser()
config.read("vietcong.ini")
db = MySQLDatabase("vietcong", **config["db"])
db.connect()

class BaseModel(Model):
	class Meta:
		database = db

class Server(BaseModel):
	ip = CharField()
	port = IntegerField(null = True)
	
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


class Player(BaseModel):
	name = CharField()
	ping = IntegerField()
	frags = IntegerField()
	
	server = ForeignKeyField(Server, related_name = "players",
		on_update = "cascade", on_delete = "cascade")

def createTables():
	Server.create_table()
	Player.create_table()


def saveServers(servers):
	db.set_autocommit(False)
	Server.delete().execute()
	for server in servers:
		serverDb = Server(**server)
		serverDb.save()
		if "players" in server:
			for player in server["players"]:
				playerDb = Player(**player)
				playerDb.server = serverDb
				playerDb.save()
	db.commit()


################################################################################
## RUN:

servers = getAll()
saveServers(servers)


