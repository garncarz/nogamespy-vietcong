#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from lxml import etree
import socket
import re

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
		"map": 11,
		"password": 7,
		"country": 8,
		"version": 9,
		"mode": 12,
		"players": 13,
		"maxplayers": 14,
		"hradba": 6 }

	servers = []
	for row in rows:
		server = {}
		for column, order in columns.items():
			value = row[order].text
			if value and value.isdigit(): value = int(value)
			server[column] = value
		servers.append(server)
	
	return servers


def getServerInfo(server):
	conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	conn.settimeout(2)
	conn.connect((server["ip"], server["infoport"]))
	conn.send("\\status\\players\\".encode("utf-8"))
	return conn.recv(4096).decode("utf-8")

def parseServerInfo(data):
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))

def mergeServerInfo(server, serverInfo):
	server["port"] = serverInfo["hostport"]
	server["dedic"] = True if "dedic" in serverInfo else False
	server["vietnam"] = True if "vietnam" in serverInfo else False
	
	columns = {
		"name": "player",
		"ping": "ping",
		"frags": "frags" }
	players = []
	for i in range(int(serverInfo["numplayers"])):
		try:
			player = {}
			for column, columnInfo in columns.items():
				player[column] = serverInfo[columnInfo + "_" + str(i)]
			players.append(player)
		except KeyError:
			break
	server["players"] = players


def getAll():
	servers = parseServersList(getServersListFile())
	for server in servers:
		try:
			mergeServerInfo(server, parseServerInfo(getServerInfo(server)))
		except socket.timeout:
			continue
	return servers


print(getAll())




