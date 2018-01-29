from cpython.version cimport PY_MAJOR_VERSION
from libtiledb cimport *
from common cimport *

cdef unicode ustring(s):
    if type(s) is unicode:
        return <unicode> s
    elif PY_MAJOR_VERSION < 3 and isinstance(s, bytes):
        return (<bytes> s).decode('ascii')
    elif isinstance(s, unicode):
        return unicode(s)
    raise TypeError(
        "ustring() must be a string or a bytes-like object"
        ", not {0!r}".format(type(s)))


cdef raise_tiledb_error(tiledb_error_t* err_ptr):
    cdef const char* err_msg_ptr = NULL
    ret = tiledb_error_message(err_ptr, &err_msg_ptr)
    if ret != TILEDB_OK:
        tiledb_error_free(err_ptr)
        if ret == TILEDB_OOM:
            return MemoryError()
        raise TileDBError("error retrieving error message")
    cdef unicode message_string = err_msg_ptr.decode('UTF-8', 'strict')
    tiledb_error_free(err_ptr)
    raise TileDBError(message_string)


cdef raise_ctx_err(tiledb_ctx_t* ctx_ptr, int rc):
    if rc == TILEDB_OK:
        return
    if rc == TILEDB_OOM:
        raise MemoryError()
    cdef int ret
    cdef tiledb_error_t* err_ptr = NULL
    ret = tiledb_ctx_get_last_error(ctx_ptr, &err_ptr)
    if ret != TILEDB_OK:
        tiledb_error_free(err_ptr)
        if ret == TILEDB_OOM:
            raise MemoryError()
        raise TileDBError("error retrieving error object from ctx")
    raise_tiledb_error(err_ptr)
