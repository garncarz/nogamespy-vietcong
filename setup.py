#!/usr/bin/python

# Copyright (C) 2014 Ondřej Garncarz 
# License: AGPLv3+

from distutils.core import setup, Extension

setup(name = "vietcong_aluigi", ext_modules = [
	Extension("aluigi", ["aluigiModule.c",
		"enctype2_decoder.c", "enctype_shared.c"])])

