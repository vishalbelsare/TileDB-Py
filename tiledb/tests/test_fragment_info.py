import itertools

import numpy as np
import pytest

import tiledb
from tiledb.main import PyFragmentInfo
from tiledb.tests.common import DiskTestCase


class FragmentInfoTest(DiskTestCase):
    def setUp(self):
        super().setUp()
        if not tiledb.libtiledb.version() >= (2, 2):
            pytest.skip("Only run FragmentInfo test with TileDB>=2.2")

    def test_uri_dne(self):
        with self.assertRaises(tiledb.TileDBError):
            fragment_info = tiledb.array_fragments("does_not_exist")

    def test_array_fragments(self):
        fragments = 3

        A = np.zeros(fragments)

        uri = self.path("test_dense_fragments")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), tile=fragments, dtype=np.int64))
        att = tiledb.Attr(dtype=A.dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,))

        tiledb.DenseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1
            with tiledb.DenseArray(uri, mode="w", timestamp=timestamp) as T:
                T[fragment_idx : fragment_idx + 1] = fragment_idx

        fragments_info = tiledb.array_fragments(uri)

        self.assertEqual(len(fragments_info), 3)
        self.assertEqual(fragments_info.unconsolidated_metadata_num, 3)

        self.assertEqual(fragments_info.cell_num, (3, 3, 3))
        self.assertEqual(
            fragments_info.has_consolidated_metadata, (False, False, False)
        )
        self.assertEqual(
            fragments_info.nonempty_domain, (((0, 0),), ((1, 1),), ((2, 2),))
        )
        self.assertEqual(fragments_info.sparse, (False, False, False))
        self.assertEqual(fragments_info.timestamp_range, ((1, 1), (2, 2), (3, 3)))
        self.assertEqual(fragments_info.to_vacuum, ())

        for idx, frag in enumerate(fragments_info):
            self.assertEqual(frag.cell_num, 3)
            self.assertEqual(frag.has_consolidated_metadata, False)
            self.assertEqual(frag.nonempty_domain, ((idx, idx),))
            self.assertEqual(frag.sparse, False)
            self.assertEqual(frag.timestamp_range, (idx + 1, idx + 1))

            if tiledb.libtiledb.version() < (2, 2, 3):
                assert frag.version == 7
            elif tiledb.libtiledb.version() < (2, 3, 0):
                assert frag.version == 8
            else:
                # make sure the version is within some reasonable bound
                # but don't pin because that makes testing against dev
                # more difficult
                assert frag.version >= 9
                assert frag.version < 12

    def test_array_fragments_var(self):
        fragments = 3

        uri = self.path("test_array_fragments_var")
        dom = tiledb.Domain(
            tiledb.Dim(name="dim", domain=(None, None), tile=None, dtype=np.bytes_)
        )
        schema = tiledb.ArraySchema(
            domain=dom,
            sparse=True,
            attrs=[tiledb.Attr(name="1s", dtype=np.int32, var=True)],
        )

        tiledb.SparseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1

            data = np.array(
                [
                    np.array([timestamp] * 1, dtype=np.int32),
                    np.array([timestamp] * 2, dtype=np.int32),
                    np.array([timestamp] * 3, dtype=np.int32),
                ],
                dtype="O",
            )

            with tiledb.SparseArray(uri, mode="w", timestamp=timestamp) as T:
                T[["zero", "one", "two"]] = data

        fragments_info = tiledb.array_fragments(uri)

        self.assertEqual(
            fragments_info.nonempty_domain,
            ((("one", "zero"),), (("one", "zero"),), (("one", "zero"),)),
        )

        for frag in fragments_info:
            self.assertEqual(frag.nonempty_domain, (("one", "zero"),))

    def test_dense_fragments(self):
        fragments = 3

        A = np.zeros(fragments)

        uri = self.path("test_dense_fragments")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), tile=fragments, dtype=np.int64))
        att = tiledb.Attr(dtype=A.dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,))

        tiledb.DenseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1
            with tiledb.DenseArray(uri, mode="w", timestamp=timestamp) as T:
                T[fragment_idx : fragment_idx + 1] = fragment_idx

            fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())
            self.assertEqual(fragment_info.get_num_fragments(), fragment_idx + 1)

        all_expected_uris = []
        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1

            self.assertEqual(
                fragment_info.get_timestamp_range()[fragment_idx],
                (timestamp, timestamp),
            )

            expected_uri = "__{ts}_{ts}".format(uri=uri, ts=timestamp)
            actual_uri = fragment_info.get_uri()[fragment_idx]

            all_expected_uris.append(expected_uri)

            # use .contains because the protocol can vary
            self.assertTrue(expected_uri in actual_uri)
            self.assertTrue(
                actual_uri.endswith(str(fragment_info.get_version()[fragment_idx]))
            )
            self.assertFalse(fragment_info.get_sparse()[fragment_idx])

        all_actual_uris = fragment_info.get_uri()
        for actual_uri, expected_uri in zip(all_actual_uris, all_expected_uris):
            self.assertTrue(expected_uri in actual_uri)
            self.assertTrue(
                actual_uri.endswith(str(fragment_info.get_version()[fragment_idx]))
            )

        self.assertEqual(fragment_info.get_timestamp_range(), ((1, 1), (2, 2), (3, 3)))
        self.assertEqual(fragment_info.get_sparse(), (False, False, False))
        if tiledb.libtiledb.version() < (2, 2, 3):
            assert fragment_info.get_version()[0] == 7
        elif tiledb.libtiledb.version() < (2, 3, 0):
            assert fragment_info.get_version()[0] == 8
        else:
            # make sure the version is within some reasonable bound
            # but don't pin because that makes testing against dev
            # more difficult
            assert fragment_info.get_version()[0] >= 9
            assert fragment_info.get_version()[0] < 12

    def test_sparse_fragments(self):
        fragments = 3

        A = np.zeros(fragments)

        uri = self.path("test_sparse_fragments")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), tile=fragments, dtype=np.int64))
        att = tiledb.Attr(dtype=A.dtype)
        schema = tiledb.ArraySchema(sparse=True, domain=dom, attrs=(att,))

        tiledb.SparseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1
            with tiledb.SparseArray(uri, mode="w", timestamp=timestamp) as T:
                T[fragment_idx] = fragment_idx

            fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())
            self.assertEqual(fragment_info.get_num_fragments(), fragment_idx + 1)

        all_expected_uris = []
        for fragment_idx in range(fragments):
            timestamp = fragment_idx + 1

            self.assertEqual(
                fragment_info.get_timestamp_range()[fragment_idx],
                (timestamp, timestamp),
            )

            if uri[0] != "/":
                uri = "/" + uri.replace("\\", "/")

            expected_uri = "/__{ts}_{ts}".format(uri=uri, ts=timestamp)
            actual_uri = fragment_info.get_uri()[fragment_idx]

            all_expected_uris.append(expected_uri)

            self.assertTrue(expected_uri in actual_uri)
            self.assertTrue(
                actual_uri.endswith(str(fragment_info.get_version()[fragment_idx]))
            )
            self.assertTrue(fragment_info.get_sparse()[fragment_idx])

        all_actual_uris = fragment_info.get_uri()
        for actual_uri, expected_uri in zip(all_actual_uris, all_expected_uris):
            self.assertTrue(expected_uri in actual_uri)
            self.assertTrue(
                actual_uri.endswith(str(fragment_info.get_version()[fragment_idx]))
            )

        self.assertEqual(fragment_info.get_timestamp_range(), ((1, 1), (2, 2), (3, 3)))
        self.assertEqual(fragment_info.get_sparse(), (True, True, True))
        if tiledb.libtiledb.version() < (2, 2, 3):
            assert fragment_info.get_version()[0] == 7
        elif tiledb.libtiledb.version() < (2, 3, 0):
            assert fragment_info.get_version()[0] == 8
        else:
            # make sure the version is within some reasonable bound
            # but don't pin because that makes testing against dev
            # more difficult
            assert fragment_info.get_version()[0] >= 9
            assert fragment_info.get_version()[0] < 12

    def test_nonempty_domain(self):
        uri = self.path("test_nonempty_domain")
        dom = tiledb.Domain(
            tiledb.Dim(name="x", domain=(1, 4)),
            tiledb.Dim(name="y", domain=(-2.0, 2.0), dtype=np.float32),
        )
        att = tiledb.Attr()
        schema = tiledb.ArraySchema(sparse=True, domain=dom, attrs=(att,))

        tiledb.SparseArray.create(uri, schema)

        with tiledb.SparseArray(uri, mode="w") as T:
            coords = np.array(
                list(itertools.product(np.arange(1, 5), np.arange(-1, 3)))
            )
            x = coords[:, 0]
            y = coords[:, 1]
            T[x, y] = np.array(range(16))

        with tiledb.SparseArray(uri, mode="w") as T:
            x = [1, 3]
            y = [-1.5, -1.25]
            T[x, y] = np.array(range(2))

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(
            fragment_info.get_nonempty_domain(),
            (((1, 4), (-1.0, 2.0)), ((1, 3), (-1.5, -1.25))),
        )

    def test_nonempty_domain_date(self):
        uri = self.path("test_nonempty_domain")
        dom = tiledb.Domain(
            tiledb.Dim(
                name="day",
                domain=(np.datetime64("2010-01-01"), np.datetime64("2020")),
                dtype="datetime64[D]",
            )
        )
        att = tiledb.Attr()
        schema = tiledb.ArraySchema(sparse=True, domain=dom, attrs=(att,))

        tiledb.SparseArray.create(uri, schema)

        with tiledb.SparseArray(uri, mode="w") as T:
            dates = np.array(
                ["2017-04-01", "2019-10-02", "2019-10-03", "2019-12-04"],
                dtype="datetime64[D]",
            )
            T[dates] = np.array(range(4))

        with tiledb.SparseArray(uri, mode="w") as T:
            dates = np.array(
                ["2010-01-01", "2013-10-02", "2014-10-03"], dtype="datetime64[D]"
            )
            T[dates] = np.array(range(3))

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(
            fragment_info.get_nonempty_domain(),
            (
                ((np.datetime64("2017-04-01"), np.datetime64("2019-12-04")),),
                ((np.datetime64("2010-01-01"), np.datetime64("2014-10-03")),),
            ),
        )

    def test_nonempty_domain_strings(self):
        uri = self.path("test_nonempty_domain_strings")
        dom = tiledb.Domain(
            tiledb.Dim(name="x", domain=(None, None), dtype=np.bytes_),
            tiledb.Dim(name="y", domain=(None, None), dtype=np.bytes_),
        )
        att = tiledb.Attr()
        schema = tiledb.ArraySchema(sparse=True, domain=dom, attrs=(att,))

        tiledb.SparseArray.create(uri, schema)

        with tiledb.SparseArray(uri, mode="w") as T:
            x_dims = [b"a", b"b", b"c", b"d"]
            y_dims = [b"e", b"f", b"g", b"h"]
            T[x_dims, y_dims] = np.array([1, 2, 3, 4])

        with tiledb.SparseArray(uri, mode="w") as T:
            x_dims = [b"a", b"b"]
            y_dims = [b"e", b"f"]
            T[x_dims, y_dims] = np.array([1, 2])

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(
            fragment_info.get_nonempty_domain(),
            ((("a", "d"), ("e", "h")), (("a", "b"), ("e", "f"))),
        )

    def test_cell_num(self):
        uri = self.path("test_cell_num")
        dom = tiledb.Domain(tiledb.Dim(domain=(1, 4)))
        att = tiledb.Attr()
        schema = tiledb.ArraySchema(sparse=True, domain=dom, attrs=(att,))

        tiledb.SparseArray.create(uri, schema)

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        with tiledb.SparseArray(uri, mode="w") as T:
            a = np.array([1, 2, 3, 4])
            T[a] = a

        with tiledb.SparseArray(uri, mode="w") as T:
            b = np.array([1, 2])
            T[b] = b

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(fragment_info.get_cell_num(), (len(a), len(b)))

    def test_consolidated_fragment_metadata(self):
        fragments = 3

        A = np.zeros(fragments)

        uri = self.path("test_consolidated_fragment_metadata")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), dtype=np.int64))
        att = tiledb.Attr(dtype=A.dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,))

        tiledb.DenseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            with tiledb.DenseArray(uri, mode="w") as T:
                T[fragment_idx : fragment_idx + 1] = fragment_idx

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(fragment_info.get_unconsolidated_metadata_num(), 3)
        self.assertEqual(
            fragment_info.get_has_consolidated_metadata(), (False, False, False)
        )

        tiledb.consolidate(
            uri, config=tiledb.Config(params={"sm.consolidation.mode": "fragment_meta"})
        )

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        self.assertEqual(fragment_info.get_unconsolidated_metadata_num(), 0)
        self.assertEqual(
            fragment_info.get_has_consolidated_metadata(), (True, True, True)
        )

    def test_fragments_to_vacuum(self):
        fragments = 3

        A = np.zeros(fragments)

        uri = self.path("test_fragments_to_vacuum")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), dtype=np.int64))
        att = tiledb.Attr(dtype=A.dtype)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,))

        tiledb.DenseArray.create(uri, schema)

        for fragment_idx in range(fragments):
            with tiledb.DenseArray(uri, mode="w") as T:
                T[fragment_idx : fragment_idx + 1] = fragment_idx

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        expected_vacuum_uri = fragment_info.get_uri()[0]

        tiledb.consolidate(
            uri, config=tiledb.Config(params={"sm.vacuum.mode": "fragments"})
        )

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        assert len(fragment_info.get_to_vacuum()) == 3
        assert fragment_info.get_to_vacuum()[0] == expected_vacuum_uri

        tiledb.vacuum(uri)

        fragment_info = PyFragmentInfo(uri, schema, False, tiledb.default_ctx())

        assert len(fragment_info.get_to_vacuum()) == 0

    @pytest.mark.skipif(
        tiledb.libtiledb.version() < (2, 5, 0),
        reason="MBRs in FragmentInfo only availabe in ilbtiledb<=2.5.0",
    )
    def test_get_mbr(self):
        fragments = 3

        uri = self.path("test_get_mbr")
        dom = tiledb.Domain(tiledb.Dim(domain=(0, 2), tile=fragments, dtype=np.int64))
        att = tiledb.Attr(dtype=np.uint64)
        schema = tiledb.ArraySchema(domain=dom, attrs=(att,), sparse=True)
        tiledb.Array.create(uri, schema)

        for fragi in range(fragments):
            timestamp = fragi + 1
            with tiledb.open(uri, mode="w", timestamp=timestamp) as T:
                T[np.array(range(0, fragi + 1))] = [fragi] * (fragi + 1)

        expected_mbrs = ((((0, 0),),), (((0, 1),),), (((0, 2),),))

        py_fragment_info = PyFragmentInfo(uri, schema, True, tiledb.default_ctx())
        assert py_fragment_info.get_mbrs() == expected_mbrs

        array_fragments = tiledb.array_fragments(uri)
        with pytest.raises(AttributeError) as excinfo:
            array_fragments.mbrs
        assert "retrieving minimum bounding rectangles is disabled" in str(
            excinfo.value
        )

        with self.assertRaises(AttributeError):
            array_fragments[0].mbrs
        assert "retrieving minimum bounding rectangles is disabled" in str(
            excinfo.value
        )

        array_fragments = tiledb.array_fragments(uri, include_mbrs=True)
        assert array_fragments.mbrs == expected_mbrs
        assert array_fragments[0].mbrs == expected_mbrs[0]
        assert array_fragments[1].mbrs == expected_mbrs[1]
        assert array_fragments[2].mbrs == expected_mbrs[2]
