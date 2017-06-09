"""
Unit tests fro tiledb
=====================

"""

import os
import sys
import unittest

def suite():
    """Collects all files in the current test/ directory"""
    testdir = os.path.dirname(__file__)
    return unittest.TestLoader().discover(
        start_dir=testdir, pattern="test_*.py")

def test(verbosity=2):
    """
    Run all the tests in the test suite.
    """
    ret = unittest.TextTestRunner(verbosity=verbosity).run(suite())
    assert(ret.wasSuccessful())
