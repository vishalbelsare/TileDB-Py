from .libtiledb import DenseArrayImpl, SparseArrayImpl


# TODO ugly, clean this up
class CloudMixinOnce(object):

    def __init__(self):
        try:
            from tiledb.cloud import cloudarray
            CloudMixinOnce.has_cloud_mixin = True
        except ImportError:
            CloudMixinOnce.has_cloud_mixin = False
        CloudMixinOnce.is_initialized = True

CloudMixinOnce.is_initialized = False
CloudMixinOnce.has_cloud_mixin = False

def init_cloud_mixin():
    if not CloudMixinOnce.is_initialized:
        CloudMixinOnce()
        return CloudMixinOnce.has_cloud_mixin
    return False


class DenseArray(DenseArrayImpl):

    def __new__(cls, *args, **kwargs):
        if init_cloud_mixin():
            from tiledb.cloud import cloudarray
            DenseArray.__bases__ = (*DenseArray.__bases__, cloudarray.CloudArray)

        obj = super().__new__(cls, *args, **kwargs)
        return obj

class SparseArray(SparseArrayImpl):
    def __new__(cls, *args, **kwargs):
        if init_cloud_mixin():
            from tiledb.cloud import cloudarray
            SparseArray.__bases__ = (*SparseArray.__bases__, cloudarray.CloudArray)

        obj = super().__new__(cls, *args, **kwargs)
        return obj
