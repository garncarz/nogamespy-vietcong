# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

from peewee import *
from datetime import datetime

import logging
logger = logging.getLogger("peewee")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())

db = Proxy()

class BaseModel(Model):
	class Meta:
		database = db

class Server(BaseModel):
	ip = CharField()
	infoport = IntegerField()
	port = IntegerField()
	
	name = CharField()
	mapname = CharField()
	mode = CharField()
	country = CharField(null = True)
	countryname = CharField(null = True)
	
	version = CharField()
	hradba = CharField(null = True)
	numplayers = IntegerField()
	maxplayers = IntegerField()
	
	password = BooleanField(null = True)
	dedic = BooleanField(null = True)
	vietnam = BooleanField(null = True)
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)
	offlineSince = DateTimeField(null = True)


class Player(BaseModel):
	name = CharField()
	ping = IntegerField()
	frags = IntegerField()
	
	server = ForeignKeyField(Server, related_name = "players",
		on_update = "cascade", on_delete = "cascade")
	
	online = BooleanField(default = True)
	onlineSince = DateTimeField(default = datetime.now)


def recreateTables():
	Player.drop_table(True, True)
	Server.drop_table(True, True)
	
	Server.create_table(True)
	Player.create_table(True)

