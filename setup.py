#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

ext_modules = [ Extension("credis.base", ["credis/base.c"])
              , Extension("credis.geventpool", ["credis/geventpool.c"])
              ]

setup(
    name = 'redis-cy',
    packages=['credis'],
    ext_modules = ext_modules,
)
