import tiledb
from unittest import TestCase

LIBVER = (0, 6, 0)

class LibTileDBTest(TestCase):

    def test_version_info(self):
        ver = tiledb.libtiledb_version_info()
        self.assertIsInstance(ver, tuple)
        self.assertEqual(ver, LIBVER)

    def test_version(self):
       self.assertEqual(tiledb.libtiledb_version(), ".".join(map(str, LIBVER)))
