#!/usr/bin/env python

# Copyright (C) 2014 Ondřej Garncarz
# License: AGPLv3+

import argparse
from datetime import datetime, timedelta

from init import *
from model import *
import listFetcher
import serverFetcher


parser = argparse.ArgumentParser(description = "VC 1 servers info crawler")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("--new", action = "store_true",
	help = "Try to find new servers")
group.add_argument("--refresh", action = "store_true",
	help = "Refresh info for all servers")
group.add_argument("--register", metavar = ("IP", "PORT"), nargs = 2,
	help = "Register new game")
group.add_argument("--recreate", action = "store_true",
	help = "Recreate DB tables")


################################################################################
## MAIN:


def findNew():
	#servers = listFetcher.callAluigi()
	#servers = listFetcher.getGameSpyList()
	servers = listFetcher.getQtrackerList()
	listFetcher.fetchNewServers(servers)
	db.commit()


def refreshAll():
	servers = Server.select()

	Server.update(online = False).execute()
	Player.update(online = False).execute()

	for server in servers:
		serverFetcher.fetchServer(server)

	#Server.update(offlineSince = datetime.now()).where((Server.online == False)
	#	& (Server.offlineSince >> None)).execute()
	#Server.delete().where(datetime.now() - Server.offlineSince >
	#	timedelta(hours = 1)).execute()
	Server.delete().where(Server.online == False).execute()
	Player.delete().where(Player.online == False).execute()
	db.commit()


def register(ip, port):
	server = Server(ip = ip, infoport = int(port))
	if Server.select().where(Server.ip == server.ip,
			Server.infoport == server.infoport).exists():
		print("EXISTS")
		return

	if serverFetcher.fetchServer(server) == False:
		print("FAIL")
		return
	db.commit()
	print("OK")


################################################################################
## RUN:

if __name__ == "__main__":
	args = parser.parse_args()
	if args.new:
		findNew()
	if args.refresh:
		refreshAll()
	if args.register:
		register(*args.register)
	if args.recreate:
		recreateTables()

