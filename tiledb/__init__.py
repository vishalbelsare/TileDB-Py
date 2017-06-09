import sys
import ctypes
from os import path

from tiledb import libtiledb

from tiledb.tests import test

def libtiledb_version_info():
    """Returns a tuple (major, minor, rev) of the libtiledb library"""
    return libtiledb.version()
    
def libtiledb_version():
    return "{:d}.{:d}.{:d}".format(*libtiledb.version())
