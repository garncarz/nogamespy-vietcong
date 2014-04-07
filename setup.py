#!/usr/bin/python

from distutils.core import setup, Extension

setup(name = "vietcong_aluigi", ext_modules = [
	Extension("aluigi", ["aluigiModule.c",
		"enctype2_decoder.c", "enctype_shared.c"])])

