# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

import os, sys
import configparser

from model import *


os.chdir(os.path.dirname(sys.argv[0]))

config = configparser.ConfigParser()
config.read("vietcong.ini")

db.initialize(MySQLDatabase("vietcong", autocommit = False, **config["db"]))
db.connect()

