#!/usr/bin/env python

"""
    This is the main setup script for tiledb
"""
from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    name="tiledb",
    ext_modules=cythonize(Extension("tiledb.libtiledb", ["tiledb/libtiledb.pyx"], 
                          libraries=["tiledb"],
                          language="c++"))
)
