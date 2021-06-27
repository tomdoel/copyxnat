# coding=utf-8

"""Factory for creating backend objects for XNAT communication"""

from copyxnat.xnat_backend.pyxnat_server import PyXnatServer
from copyxnat.xnat_backend.xnatpy_server import XnatPyServer


class ServerFactory(object):
    """Factory for creating XNAT backend objects"""

    def __init__(self, backend):
        self._backend = backend

    def create(self, params):
        """
        Create an XNAT server backend object
        @param params: XnatServerParams for the XNAT server
        @return: a server backend for communicating with XnatInterface
        """
        if self._backend.lower() == 'pyxnat':
            return PyXnatServer(params=params)
        elif self._backend.lower() == 'xnatpy':
            return XnatPyServer(params=params)
        else:
            ValueError('Unknown backend {}'.format(self._backend))
