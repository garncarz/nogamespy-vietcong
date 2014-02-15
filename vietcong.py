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

def parseServersList(data):
	tree = etree.parse(data, parser = etree.HTMLParser())
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
		"hradba": 6
	}

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
	conn.connect((server["ip"], server["infoport"]))
	conn.send("\\status\\players\\".encode("utf-8"))
	return conn.recv(4096).decode("utf-8")

def parseServerInfo(data):
	arr = re.split("\\\\", data)[1:-4]
	return dict(zip(arr[::2], arr[1::2]))


# f = open("list.html", "r")
f = getServersListFile()
servers = parseServersList(f)
servers = list(filter(lambda s: s["players"] > 0, servers))
print(servers)
print(parseServerInfo(getServerInfo(servers[1])))

