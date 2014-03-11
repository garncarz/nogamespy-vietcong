#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import configparser

from model import *


os.chdir(os.path.dirname(sys.argv[0]))

config = configparser.ConfigParser()
config.read("vietcong.ini")

db.initialize(MySQLDatabase("vietcong", **config["db"]))
db.connect()

