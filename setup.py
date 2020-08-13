#!/usr/bin/env python
try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup

from distutils.extension import Extension

from Cython.Distutils import build_ext

ext_modules = [
    Extension("credis.base", ["credis/base.pyx"]),
    Extension("credis.geventpool", ["credis/geventpool.pyx"]),
]
cmdclass = {"build_ext": build_ext}

setup(
    name="credis",
    version="2.0.0",
    packages=["credis"],
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    author="huangyi",
    author_email="yi.codeplayer@gmail.com",
    url="https://github.com/yihuang/credis",
    description="high performance redis client implemented with cython",
    long_description=open("README.rst").read(),
    install_requires=["hiredis >= 1.1.0",],
    platforms=[],
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Cython",
        "Topic :: Database",
    ],
)
