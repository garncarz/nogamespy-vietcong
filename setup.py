#!/usr/bin/env python3

from distutils.core import setup, Extension

setup(
    name='nogamespy',
    ext_modules=[
        Extension(
            'aluigi',
            ['aluigi/aluigiModule.c',
             'aluigi/enctype2_decoder.c',
             'aluigi/enctype_shared.c',
             ],
        )
    ],
)
