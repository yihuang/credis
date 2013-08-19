#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

ext_modules = [ Extension("credis", ["credis.c"])
              ]

setup(
    name = 'redis-cy',
    ext_modules = ext_modules,
)
