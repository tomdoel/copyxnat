# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import os

from requests import HTTPError

from copyxnat.xnat_backend.utis import Utils
from copyxnat.xnat_backend.xnat_session import XnatSession


class XnatRestClient(object):
    """Wrapper around XNAT REST API"""

    def __init__(self, params, read_only):
        self._session = XnatSession(params, read_only)

    def __del__(self):
        self.logout()

    def logout(self):
        """End this XNAT session"""
        self._session.logout()

    def download_file(self, uri, file_path, qs_params):
        """Download file from server to specified file location

        :param file_path: full local destination path for file
        :param uri: Relative URI of resource to download
        :param qs_params: Additional query string parameters
        """
        with self._session.request(method='get', uri=uri, qs_params=qs_params,
                                   stream=True
        ) as response:
            with open(file_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)

    def upload_file(self, method, uri, file_path, qs_params):
        """Upload file to server from the specified location

        :param method: request method (post or put)
        :param uri: Relative URI on the XNAT server
        :param file_path: full local source path for file
        :param qs_params: dictionary of querystring parameters
        """
        if not os.path.isfile(file_path):
            raise ValueError('File {} does not exist'.format(file_path))

        with open(file_path, 'rb') as file_data:
            self._session.request(method=method, uri=uri,qs_params=qs_params,
                                  body=file_data)

    def meta(self, uri):
        """Return dictionary of XNAT metadata"""
        return self._session.request(
            method='GET', uri=uri, qs_params={'format': 'json'}
        ).json().get("items")[0].get('meta')

    def request_json_property(self, uri, optional=False, qs_params=None):
        """Execute a REST call on the server and return result as list
        If optional is True, then a 404 response will yield an empty list"""
        try:
            return self._session.request(
                method='GET', uri=uri,
                qs_params=Utils.combine_dicts(qs_params, {'format': 'json'})
            ).json().get("ResultSet").get('Result')

        except HTTPError as err:
            if optional and err.response.status_code == 404:
                return []
            else:
                raise err

    def request_string(self, uri, qs_params=None):
        """Execute a REST call on the server and return string"""
        return self._session.request(
            method='GET', uri=uri, qs_params=qs_params
        ).text

    def request(self, uri, method, qs_params=None):
        """Execute a REST call on the server. Does not return response"""
        self._session.request(method=method, uri=uri, qs_params=qs_params)
