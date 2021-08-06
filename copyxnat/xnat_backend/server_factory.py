# coding=utf-8

"""Factory for creating backend objects for XNAT communication"""

from copyxnat.xnat_backend.pyxnat_server import PyXnatServer
from copyxnat.xnat_backend.simple_xnat import SimpleXnatServer


class ServerFactory(object):
    """Factory for creating XNAT backend objects"""

    def __init__(self, backend):
        self._backend = backend

    def create(self, params, read_only):
        """
        Create an XNAT server backend object
        @param params: XnatServerParams for the XNAT server
        @param read_only: if True then the server may prevent write requests
        @return: a server backend for communicating with XnatInterface
        """
        if self._backend.lower() == 'pyxnat':
            return PyXnatServer(params=params)
        elif self._backend.lower() == 'simplexnat':
            return SimpleXnatServer(params=params, read_only=read_only)
        else:
            raise ValueError('Unknown backend {}'.format(self._backend))
