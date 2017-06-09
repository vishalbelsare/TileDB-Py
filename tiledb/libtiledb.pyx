# distutils: language=c++

from cython cimport view

from libc.stdlib cimport malloc, free
from libc.string cimport memset, strcpy
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "tiledb.h":
    
    ###################
    # C Defines
    ###################
    cdef int _TILEDB_ERR "TILEDB_ERR"
    cdef int _TILEDB_OK "TILEDB_OK"

    # Array mode
    cdef int _TILEDB_ARRAY_READ "TILEDB_ARRAY_READ"
    cdef int _TILEDB_ARRAY_READ_SORTED_COL "TILEDB_ARRAY_READ_SORTED_COL"
    cdef int _TILEDB_ARRAY_READ_SORTED_ROW "TILEDB_ARRAY_READ_SORTED_ROW"
    cdef int _TILEDB_ARRAY_WRITE "TILEDB_ARRAY_WRITE"
    cdef int _TILEDB_ARRAY_WRITE_SORTED_COL "TILEDB_ARRAY_WRITE_SORTED_COL"
    cdef int _TILEDB_ARRAY_WRITE_SORTED_ROW "TILEDB_ARRAY_WRITE_SORTED_ROW"
    cdef int _TILEDB_ARRAY_WRITE_UNSORTED "TILEDB_ARRAY_WRITE_UNSORTED"

    # Metadata mode
    cdef int _TILEDB_METADATA_READ "TILEDB_METADATA_READ"
    cdef int _TILEDB_METADATA_WRITE "TILEDB_METADATA_WRITE"

    # I/O method
    cdef int _TILEDB_IO_MMAP "TILEDB_IO_MMAP"
    cdef int _TILEDB_IO_READ "TILEDB_IO_READ"
    cdef int _TILEDB_IO_MPI "TILEDB_IO_MPI"
    cdef int _TILEDB_IO_WRITE "TILEDB_IO_WRITE"

    # Asynchronous I/O (AIO) code
    cdef int _TILEDB_AIO_ERR "TILEDB_AIO_ERR"
    cdef int _TILEDB_AIO_COMPLETED "TILEDB_AIO_COMPLETED"
    cdef int _TILEDB_AIO_INPROGRESS "TILEDB_AIO_INPROGRESS"
    cdef int _TILEDB_AIO_OVERFLOW "TILEDB_AIO_OVERFLOW"
     
    # TileDB home directory
    cdef char* _TILEDB_HOME "TILEDB_HOME"

    # TileDB object type
    cdef int _TILEDB_WORKSPACE "TILEDB_WORKSPACE" 
    cdef int _TILEDB_GROUP "TILEDB_GROUP"
    cdef int _TILEDB_ARRAY "TILEDB_ARRAY" 
    cdef int _TILEDB_METADATA "TILEDB_METADATA" 

    # The maximum length for the names of TileDB objects.
    cdef int _TILEDB_NAME_MAX_LEN "TILEDB_NAME_MAX_LEN"

    # Size of the buffer used during consolidation.
    cdef int _TILEDB_CONSOLIDATION_BUFFER_SIZE "TILEDB_CONSOLIDATION_BUFFER_SIZE"

    # Special value indicating a variable number or size.
    cdef int _TILEDB_VAR_NUM "TILEDB_VAR_NUM" 
    cdef size_t _TILEDB_VAR_SIZE "TILEDB_VAR_SIZE"

    # Data types
    cdef int _TILEDB_INT32 "TILEDB_INT32"
    cdef int _TILEDB_INT64 "TILEDB_INT64"
    cdef int _TILEDB_FLOAT32 "TILEDB_FLOAT32"
    cdef int _TILEDB_FLOAT64 "TILEDB_FLOAT64"
    cdef int _TILEDB_CHAR "TILEDB_CHAR"
    cdef int _TILEDB_INT8 "TILEDB_INT8"
    cdef int _TILEDB_UINT8 "TILEDB_UINT8"
    cdef int _TILEDB_INT16 "TILEDB_INT16"
    cdef int _TILEDB_UINT16 "TILEDB_UINT16"
    cdef int _TILEDB_UINT32 "TILEDB_UINT32"
    cdef int _TILEDB_UINT64 "TILEDB_UINT64"

    # Tile or cell order
    cdef int _TILEDB_ROW_MAJOR "TILEDB_ROW_MAJOR"
    cdef int _TILEDB_COL_MAJOR "TILEDB_COL_MAJOR"

    # Compression type
    cdef int _TILEDB_NO_COMPRESSION "TILEDB_NO_COMPRESSION"
    cdef int _TILEDB_GZIP "TILEDB_GZIP"
    cdef int _TILEDB_ZSTD "TILEDB_ZSTD"
    cdef int _TILEDB_LZ4 "TILEDB_LZ4"
    cdef int _TILEDB_BLOSC "TILEDB_BLOSC"
    cdef int _TILEDB_BLOSC_LZ4 "TILEDB_BLOSC_LZ4"
    cdef int _TILEDB_BLOSC_LZ4HC "TILEDB_BLOSC_LZ4HC"
    cdef int _TILEDB_BLOSC_SNAPPY "TILEDB_BLOSC_SNAPPY"
    cdef int _TILEDB_BLOSC_ZLIB "TILEDB_BLOSC_ZLIB"
    cdef int _TILEDB_BLOSC_ZSTD "TILEDB_BLOSC_ZSTD"
    cdef int _TILEDB_RLE "TILEDB_RLE"
    cdef int _TILEDB_BZIP2 "TILEDB_BZIP2"

    # Special attribute name
    cdef char* _TILEDB_COORDS "TILEDB_COORDS"
    cdef char* _TILEDB_KEY "TILEDB_KEY"
    
    # Special TileDB file name suffix
    cdef char* _TILEDB_FILE_SUFFIX "TILEDB_FILE_SUFFIX"
    cdef char* _TILEDB_GZIP_SUFFIX "TILEDB_GZIP_SUFFIX"

    # Chunk size in GZIP decompression.
    cdef int _TILEDB_GZIP_CHUNK_SIZE  "TILEDB_GZIP_CHUNK_SIZE"

    # Special TileDB file name. */
    cdef char* _TILEDB_ARRAY_SCHEMA_FILENAME "TILEDB_ARRAY_SCHEMA_FILENAME"
    cdef char* _TILEDB_METADATA_SCHEMA_FILENAME "TILEDB_METADATA_SCHEMA_FILENAME"
    cdef char* _TILEDB_BOOK_KEEPING_FILENAME "TILEDB_BOOK_KEEPING_FILENAME"
    cdef char* _TILEDB_FRAGMENT_FILENAME "TILEDB_FRAGMENT_FILENAME"
    cdef char* _TILEDB_GROUP_FILENAME "TILEDB_GROUP_FILENAME"
    cdef char* _TILEDB_WORKSPACE_FILENAME "TILEDB_WORKSPACE_FILENAME"

    # Size of buffer used for sorting. */
    cdef int _TILEDB_SORTED_BUFFER_SIZE "TILEDB_SORTED_BUFFER_SIZE"
    cdef int _TILEDB_SORTED_BUFFER_VAR_SIZE "TILEDB_SORTED_BUFFER_VAR_SIZE"
    
    ##########################
    # TileDB exported globals
    ##########################
    cdef char* tiledb_errmsg

    ###########################
    # TileDB Struct Definitions
    ###########################
    
    ctypedef struct TileDB_Config:
        char* home_
        int read_method_
        int write_method_
    
    ctypedef struct TileDB_CTX:
        pass

    ctypedef struct TileDB_ArraySchema:
        pass

    ############################
    # TileDB Method Definitions
    ############################
    int tiledb_ctx_init(TileDB_CTX** ctx, TileDB_Config* config)
    int tiledb_ctx_finalize(TileDB_CTX* ctx)

    int tiledb_workspace_create(TileDB_CTX*, const char* path)
    int tiledb_group_create(TileDB_CTX*, const char* path)
    
    int tiledb_array_set_schema(TileDB_ArraySchema* sch,
                                const char* array_name,
                                char** attributes,
                                int attribute_num,
                                long capacity,
                                int cell_order,
                                const int* cell_val_num,
                                const int* compression,
                                int dense,
                                char** dimensions,
                                int dim_num,
                                const void* domain,
                                size_t domain_len,
                                const void* tile_extents,
                                size_t tile_extents_len,
                                int tile_order,
                                const int* types)
    int tiledb_array_create(TileDB_CTX* ctx, TileDB_ArraySchema* sch)
    int tiledb_array_free_schema(TileDB_ArraySchema* sch)
    
    int tiledb_clear(const TileDB_CTX* ctx, const char* path)
    int tiledb_delete(const TileDB_CTX* ctx, const char* path) 
    int tiledb_move(const TileDB_CTX* ctx, 
                    const char* old_path,
                    const char* new_path)
    
    int tiledb_ls_workspaces(const TileDB_CTX* ctx, char** ws, int* nws)
    int tiledb_ls_workspaces_c(const TileDB_CTX* ctx, int* nws)
    
    int tiledb_ls(const TileDB_CTX* ctx, 
                  const char* parent_path, 
                  char** paths,
                  int* path_types,
                  int* path_num)
    int tiledb_ls_c(const TileDB_CTX* ctx, 
                    const char* parent_path,
                    int* path_num)

    void tiledb_version(int* major, int* minor, int* rev)

def _tiledb_compressor(compress):
    if compress is None:
        return _TILEDB_NO_COMPRESSION
    elif compress is "gzip":
        return _TILEDB_GZIP
    elif compress is "zstd":
        return _TILEDB_ZSTD
    elif compress is "lz4":
        return _TILEDB_LZ4
    elif compress is "blosc":
        return _TILEDB_BLOSC
    elif compress is "blosc_lz4":
        return _TILEDB_BLOSC_LZ4
    elif compress is "blosc_lz4hc":
        return _TILEDB_BLOSC_LZ4HC
    elif compress is "blosc_snappy":
        return _TILEDB_BLOSC_SNAPPY
    elif compress is "blosc_zlib":
        return _TILEDB_BLOSC_ZLIB
    elif compress is "blosc_zstd":
        return _TILEDB_BLOSC_ZSTD
    elif compress is "rle":
        return _TILEDB_RLE
    elif compress is "bzip2":
        return _TILEDB_BZIP2
    else:
        raise AttributeError("compressor `{}` is not supported".format(compress))

def _tiledb_dtype(dtype):
    if dtype is "var":
        return _TILEDB_VAR_SIZE
    elif dtype is "int32":
        return _TILEDB_INT32
    elif dtype is "int64":
        return _TILEDB_INT64
    elif dtype is "float32":
        return _TILEDB_FLOAT32
    elif dtype is "float64":
        return _TILEDB_FLOAT64
    else:
        raise AttributeError("dtype `{}` is not supported".format(dtype))

def _tiledb_layout(layout):
    if layout is "rowmajor":
        return _TILEDB_ROW_MAJOR
    elif layout is "colmajor":
        return _TILEDB_COL_MAJOR
    else:
        raise AttributeError("layout must be 'rowmajor' or 'colmajor'")


cdef class TileDBError(Exception):

    def __init__(self):
        global tiledb_errmsg
        super().__init__(tiledb_errmsg.decode("UTF-8"))


cdef class Ctx(object):

    cdef TileDB_CTX* ptr 

    def __dealloc__(self):
        tiledb_ctx_finalize(self.ptr)
    
    @staticmethod
    cdef create(TileDB_CTX* ctx_ptr):
        ctx = Ctx()
        ctx.ptr = ctx_ptr
        return ctx

  
cdef class Coords(object):
    
    cdef:
        readonly int layout 
        readonly int dtype
        readonly int compressor 
        readonly int ndim
        readonly list domain
        readonly list dims

    def __cinit__(self, dims=None, domain=None, layout=None, dtype="int64", compress=None):
        if dims is None:
            raise AttributeError("must specifiy array attribute dimensions")
        if domain is None:
            raise AttributeError("domain must be specified")
        if len(dims) != len(domain):
            raise AttributeError("number of dims does not match the domain")
        self.dims = []
        for d in dims:
            if not isinstance(d, str):
                raise AttributeError("dims must be an iterable of strings")
            if len(d) > _TILEDB_NAME_MAX_LEN:
                raise AttributeError(
                    "name cannot be longer than {} characters".format(_TILEDB_NAME_MAX_LEN))
            self.dims.append(d.encode())
        self.layout = _tiledb_layout(layout)
        self.dtype = _tiledb_dtype(dtype)
        self.compressor = _tiledb_compressor(compress)
        self.ndim = len(domain)
        self.domain = []
        for d in domain:
            if len(d) != 2:
                raise AttributeError("domain must be an iterable of pairs")
            self.domain.extend(d)


cdef class Attr(object):

    cdef:
        readonly bytes name
        readonly int nval
        readonly int dtype
        readonly int compressor
    
    def __cinit__(self, name=None, nval=1, dtype=None, compress=None):
        if name is None:
            raise AttributeError("no given attribute name")
        # TODO: len(bytes) not len(characters) for unicode
        if len(name) > _TILEDB_NAME_MAX_LEN:
            raise AttributeError(
                    "name cannot be longer than {} characters"
                    .format(_TILEDB_NAME_MAX_LEN))
        self.name = name.encode()
        self.nval = _TILEDB_VAR_NUM if dtype is "var" else nval
        self.dtype = _tiledb_dtype(dtype)
        self.compressor = _tiledb_compressor(compress)


cdef char** cstring_array(strs, size_t nstrs):
    cdef bytes curstr
    cdef char** ret = <char **>malloc(nstrs * sizeof(char*))
    for i in range(nstrs):
        curstr = strs[i]
        ret[i] = <char *>malloc(len(curstr) + 1)
        strcpy(ret[i], curstr)
    return ret


cdef class ArraySchema(object):

    cdef TileDB_ArraySchema* ptr
    
    def __cinit__(self,
                  name=None,
                  coords=None,
                  attrs=None,
                  capacity=0, 
                  isdense=True,
                  tile_extents=None,
                  tile_layout=None):
        if name is None:
            raise AttributeError("must specifiy an array name")
        if coords is None:
            raise AttributeError("must specify array coordinates")
        if attrs is None or len(attrs) == 0:
            raise AttributeError("must specifiy at least one attribute")
        if not isinstance(coords, Coords):
            raise TypeError("coords must be Coords")
        if tile_extents is None:
            raise AttributeError("tile_extents must be defined")
        if tile_layout is None:
            raise AttributeError("tile_layout must be defined")
        ndims = coords.ndim
        if len(tile_extents) != ndims:
            raise AttributeError(
                    "the number of tile extents does not match the array dimension")
        
        nattr = len(attrs)
        cdef int* attr_nvals = <int *> malloc(nattr * sizeof(int))
        cdef int* attr_dtype = <int *> malloc((nattr + 1) * sizeof(int)) # coord dtype goes last
        cdef int* attr_compr = <int *> malloc((nattr + 1) * sizeof(int)) # coord compr goes last
        attr_names = []
        for i in range(nattr):
            attr = attrs[i]
            if not isinstance(attr, Attr):
                free(attr_nvals)
                free(attr_dtype)
                free(attr_compr)
                raise TypeError("attributes must be Attr")
            attr_names.append(attr.name)
            attr_nvals[i] = <int>attr.nval
            attr_dtype[i] = <int>attr.dtype
            attr_compr[i] = <int>attr.compressor
        # Fill in the dimension datatype
        attr_dtype[nattr] = coords.dtype
        attr_compr[nattr] = coords.compressor
        
        cdef int* extents = <int *>malloc(ndims * sizeof(int))
        cdef int* domains = <int *>malloc(ndims * sizeof(int)) 
        for i in range(ndims):
            extents[i] = tile_extents[i]
            domains[2*i] = coords.domain[2*i] 
            domains[2*i+1] = coords.domain[2*i+1]

        tile_layout = _tiledb_layout(tile_layout)

        cdef char** cattr_names = cstring_array(attr_names, nattr)
        cdef char** cdims_names = cstring_array(coords.dims, ndims)
        sch_ptr = <TileDB_ArraySchema *>malloc(sizeof(TileDB_ArraySchema))
        ret = tiledb_array_set_schema(
                                sch_ptr,
                                name.encode(),
                                cattr_names,
                                nattr,
                                capacity,
                                coords.layout,
                                attr_nvals,
                                attr_compr,
                                1 if isdense else 0,
                                cdims_names,
                                ndims,
                                domains,
                                (2 * ndims) * sizeof(int),
                                extents,
                                ndims * sizeof(int),
                                tile_layout,
                                attr_dtype)
        free(extents)
        free(domains)
        free(attr_nvals)
        free(attr_dtype)
        free(attr_compr)
        for i in range(nattr):
            free(cattr_names[i])
        free(cattr_names)
        for i in range(ndims):
            free(cdims_names[i])
        free(cdims_names)
        if ret != _TILEDB_OK:
            raise TileDBError()
        self.ptr = sch_ptr
        return 

    def __dealloc__(self):
        tiledb_array_free_schema(self.ptr)


def array_create(Ctx ctx, ArraySchema sch):
    ret = tiledb_array_create(ctx.ptr, sch.ptr)
    if ret != _TILEDB_OK:
        raise TileDBError()
   

def version():
    cdef:
        int major = 0
        int minor = 0
        int rev   = 0
    tiledb_version(&major, &minor, &rev)
    return (major, minor, rev)


cdef TileDB_Config* _default_config():
    cdef TileDB_Config* cfg
    cfg = <TileDB_Config *>malloc(sizeof(TileDB_Config))
    memset(cfg, 0, sizeof(TileDB_Config))
    return cfg


def ctx_init():
    cdef TileDB_CTX* ctx 
    cdef TileDB_Config* cfg = _default_config()
    rc = tiledb_ctx_init(&ctx, cfg)
    if rc != _TILEDB_OK:
        free(cfg)
        raise Exception("error message here")
    return Ctx.create(ctx)


def workspace_create(Ctx ctx, str path):
    """Creates a new TileDB workspace"""
    rc = tiledb_workspace_create(ctx.ptr, path.encode())
    if rc != _TILEDB_OK:
        raise TileDBError()


def group_create(Ctx ctx, str path):
    """Creates a new TileDB group"""
    rc = tiledb_group_create(ctx.ptr, path.encode()) 
    if rc != _TILEDB_OK:
        raise TileDBError()

def delete(Ctx ctx, str path):
    cdef bytes bpath = path.encode()
    rc = tiledb_delete(ctx.ptr, bpath)
    if rc != _TILEDB_OK:
        raise TileDBError()

def clear(Ctx ctx, str path):
    cdef bytes bpath = path.encode()
    rc = tiledb_clear(ctx.ptr, bpath)
    if rc != _TILEDB_OK:
        raise TileDBError()

def move(Ctx ctx, str old_path, str new_path):
    cdef bytes bold = old_path.encode()
    cdef bytes bnew = new_path.encode()
    rc = tiledb_move(ctx.ptr, bold, bnew)
    if rc != _TILEDB_OK:
        raise TileDBError()

def workspace_list(Ctx ctx):
    cdef int nws = 0
    rc = tiledb_ls_workspaces_c(ctx.ptr, &nws)
    if rc != _TILEDB_OK:
        raise TileDBError()
    if nws == 0:
        return []
    cdef char** cws = <char**>malloc(nws * sizeof(char*))
    for i in range(nws):
        cws[i] = <char *>malloc(_TILEDB_NAME_MAX_LEN)
    ws = []
    try:
        rc = tiledb_ls_workspaces(ctx.ptr, cws, &nws);
        if rc != _TILEDB_OK:
            raise TileDBError()
        for i in range(nws):
            ws.append((<bytes> cws[i]).decode('UTF-8'))
    finally:
        for i in range(nws):
            free(cws[i])
        free(cws)
    return ws

def _object_type_string(int objtype):
    if objtype == _TILEDB_WORKSPACE:
        return "workspace"
    elif objtype == _TILEDB_GROUP: 
        return "group"
    elif objtype == _TILEDB_ARRAY:
        return "array"
    elif objtype == _TILEDB_METADATA:
        return "metadata"
    else:
        raise AttributeError(
                "unknown TileDB object type (val: {:d})".format(objtype))

def ls(Ctx ctx, str path):
    cdef int npaths = 0
    cdef bytes bpath = path.encode()
    rc = tiledb_ls_c(ctx.ptr, bpath, &npaths)
    if rc != _TILEDB_OK:
        raise TileDBError()
    if npaths == 0:
        return []
    cdef char** paths = <char**>malloc(npaths * sizeof(char*))
    for i in range(npaths):
        paths[i] = <char*>malloc(_TILEDB_NAME_MAX_LEN)
    cdef int ptype 
    cdef int* path_types = <int*>malloc(npaths * sizeof(int))
    ret = []
    try:
        rc = tiledb_ls(ctx.ptr, bpath, paths, path_types, &npaths)
        if rc != _TILEDB_OK:
            raise TileDBError()
        for i in range(npaths):
            bpath = <bytes> paths[i]
            ret.append((bpath.encode('UTF-8'), 
                       _object_type_string(path_types[i])))
    finally:
        for i in range(npaths):
            free(paths[i])
        free(paths)
        free(path_types)
    return ret
