#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree

def parseServers(data):
	tree = etree.parse(data, parser = etree.HTMLParser())
	rows = tree.xpath("/html/body/form/table/tbody/tr")[1:]

	columns = {
		"ip": 0,
		"port": 1,
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
			server[column] = row[order].text
		servers.append(server)
	
	return servers

f = open("list.html", "r")
servers = parseServers(f)
print(servers)

