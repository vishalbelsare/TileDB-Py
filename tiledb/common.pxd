from libtiledb cimport *

cdef class TileDBError(Exception):
    pass

cdef raise_ctx_err(tiledb_ctx_t* ctx_ptr, int rc)

cdef raise_tiledb_error(tiledb_error_t* err_ptr)

cdef unicode ustring(s)