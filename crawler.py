#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import configparser
from datetime import datetime, timedelta

from model import *
from listFetcher import *
from serverFetcher import *


parser = argparse.ArgumentParser(description = "VC 1 servers' info crawler")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("--new", action = "store_true",
	help = "Try to find new servers")
group.add_argument("--refresh", action = "store_true",
	help = "Refresh info for all servers")
group.add_argument("--recreate", action = "store_true",
	help = "Recreate DB tables")

config = configparser.ConfigParser()
config.read("vietcong.ini")

db.initialize(MySQLDatabase("vietcong", **config["db"]))
db.connect()


################################################################################
## MAIN:


def fetchNewServers():
	servers = callAluigi()
	db.set_autocommit(False)
	saveNewServers(servers)
	db.commit()


def refreshAll():
	servers = Server.select()
	
	db.set_autocommit(False)
	Server.update(online = False).execute()
	Player.update(online = False).execute()
	
	for server in servers:
		fetchServer(server)
	
	Server.update(offlineSince = datetime.now()).where((Server.online == False)
		& (Server.offlineSince >> None)).execute()
	Server.delete().where(datetime.now() - Server.offlineSince >
		timedelta(hours = 1)).execute()
	Player.delete().where(Player.online == False).execute()
	db.commit()


################################################################################
## RUN:

if __name__ == "__main__":
	args = parser.parse_args()
	if args.new:
		fetchNewServers()
	if args.refresh:
		refreshAll()
	if args.recreate:
		recreateTables()

