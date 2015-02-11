#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
    have_cython = True
except ImportError:
    have_cython = False

if have_cython:
    ext_modules = [Extension("credis.base", ["credis/base.pyx"]),
                   Extension("credis.geventpool", ["credis/geventpool.pyx"]),
                   ]
    cmdclass = {'build_ext': build_ext}
else:
    cmdclass = {}
    ext_modules = [Extension("credis.base", ["credis/base.c"]),
                   Extension("credis.geventpool", ["credis/geventpool.c"]),
                   ]


setup(
    name='credis',
    version='1.0.5',
    packages=['credis'],
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    author='huangyi',
    author_email='yi.codeplayer@gmail.com',
    url='https://github.com/yihuang/credis',
    description='high performance redis client implemented with cython',
    long_description=open('README.rst').read(),
    install_requires=[
        'hiredis >= 0.1',
    ],
)
