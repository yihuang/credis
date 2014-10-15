#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

ext_modules = [ Extension("credis.base", ["credis/base.c"])
              , Extension("credis.geventpool", ["credis/geventpool.c"])
              ]

setup(
    name = 'credis',
    version = '1.0.3',
    packages=['credis'],
    ext_modules = ext_modules,
    author='huangyi',
    author_email='yi.codeplayer@gmail.com',
    url = 'https://github.com/yihuang/credis',
    description = 'high performance redis client implemented with cython',
    long_description=open('README.rst').read(),
    install_requires = [
        'hiredis >= 0.1',
    ],
)
