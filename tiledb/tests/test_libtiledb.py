import tiledb
from tiledb import libtiledb

import os
import tempfile
from unittest import TestCase

LIBVER = (0, 6, 0)

# TODO: check object id as well
def workspace_exists(path):
    return os.path.isdir(path)

def group_exists(path):
    return os.path.isdir(path)


class LibTileDBTest(TestCase):

    def test_version(self):
        ver = libtiledb.version()
        self.assertIsInstance(ver, tuple)
        self.assertEqual(ver, LIBVER)

    def test_workspace_create(self):
        tmp = tempfile.mkdtemp()
        ctx = libtiledb.ctx_init()
        wrk = os.path.join(tmp, "my_workspace")
        libtiledb.workspace_create(ctx, wrk)
        self.assertTrue(workspace_exists(wrk))

        # error is thrown when the workspace already exists
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.workspace_create(ctx, wrk)

        # error is thrown when the dir with the same name already exists
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.workspace_create(ctx, tmp)

        # error is thrown when the workspace is an empty string
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.workspace_create(ctx, "")

        # error is thrown with an invalid context
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.workspace_create(None, wrk)

        # error is thrown when the workspace arg is the wrong type
        with self.assertRaises(AttributeError):
            libtiledb.workspace_create(ctx, None)

    def test_group_create(self):
        tmp = tempfile.mkdtemp()
        ctx = libtiledb.ctx_init()

        wid = "my_workspace"
        wrk = os.path.join(tmp, wid)
        libtiledb.workspace_create(ctx, wrk)
        self.assertTrue(workspace_exists(wrk))

        # my_workspace/test1
        gid1 = "test1"
        grp1 = "/".join((wrk, gid1))
        libtiledb.group_create(ctx, grp1)
        self.assertTrue(group_exists(grp1))

        # my_workspace/test2
        gid2 = "test2"
        grp2 = "/".join((wrk, gid2))
        libtiledb.group_create(ctx, grp2)
        self.assertTrue(group_exists(grp2))

        # my_workspace/test2/test3"
        gid3 = "test3"
        grp3 = "/".join((wrk, gid2, gid3))
        libtiledb.group_create(ctx, grp3)

        # error is thrown when the group has no parent
        with self.assertRaises(libtiledb.TileDBError):
            grp4 = "/".join((wrk, "error", "test4"))
            libtiledb.group_create(ctx, grp4)

        # error is thrown when the group already exists
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.group_create(ctx, gid1)

        # error is thrown when the group is a workspace
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.group_create(ctx, wrk)

        # error is thrown when the group is empty
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.group_create(ctx, wrk + "/")

        # error is thrown when the group string is empty
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.group_create(ctx, "")

        # error is thrown with an invalid context
        with self.assertRaises(libtiledb.TileDBError):
            libtiledb.group_create(None, "/".join((wrk, "foo")))

        # error is thrown when the group arg the wrong type
        with self.assertRaises(AttributeError):
            libtiledb.group_create(ctx, None)

