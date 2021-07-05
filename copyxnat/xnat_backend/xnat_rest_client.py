# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import os

from requests import HTTPError

from copyxnat.xnat_backend.utis import Utils
from copyxnat.xnat_backend.xnat_session import XnatSession


class XnatRestClient(object):
    """Wrapper around XNAT REST API"""

    def __init__(self, params):
        self._session = XnatSession(params)

    def __del__(self):
        self.logout()

    def logout(self):
        """Return XML representation of this XNAT item"""

        self._session.logout()

    def download_file(self, file_path, uri, qs_params):
        """
        Download file from server to specified file location

        :param file_path: Destination path for file
        :param uri: Relative URI of resource to download
        :param qs_params: Additional query string parameters
        """
        with self._session.request(
                method='get',
                uri=uri,
                qs_params=qs_params,
                stream=True
        ) as response:
            response.raise_for_status()
            with open(file_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)

    def upload_file(self, method, uri, file_path, file_format=None, tags=None,
                    content=None, overwrite=False, is_zip=None):
        """
        Upload file to server from the specified location

        :param method: request method (post or put)
        :param uri: Relative URI on the XNAT server
        :param file_path: path to file to be uploaded
        :param file_format: XNAT format attribute
        :param tags: XNAT tags attribute
        :param content: XNAT content attribute
        :param overwrite: True to overwrite existing data
        :param is_zip:  True if the uploading a zip file which should be
        extracted by the server
        """
        if not os.path.isfile(file_path):
            raise ValueError('File {} does not exist'.format(file_path))
        qs_params = Utils.optional_params({'format': file_format,
                                           'content': content,
                                           'tags': tags,
                                           'overwrite': overwrite,
                                           'inbody': True,
                                           'extract': is_zip,
                                           'allowDataDeletion': 'false'})

        with open(file_path, 'rb') as file_data:
            response = self._session.request(
                method=method,
                uri=uri,
                qs_params=qs_params,
                body=file_data)
            response.raise_for_status()

    def meta(self, uri):
        """Return dictionary of XNAT metadata"""
        return self._request_json(uri=uri).get("items")[0].get('meta')

    def request_json_property(self, uri, optional=False, qs_params=None):
        """Execute a REST call on the server and return result as list
        If optional is True, then a 404 response will yield an empty list"""
        try:
            json = self._request_json(uri=uri, qs_params=qs_params)
            return json.get("ResultSet").get('Result') if json else []

        except HTTPError as err:
            if optional and err.response.status_code == 404:
                return []
            else:
                raise err

    def _request_json(self, uri, qs_params=None):
        """Execute a REST call on the server and return result as json"""
        response = self._session.request(
            method='GET',
            uri=uri,
            qs_params=Utils.combine_dicts(qs_params, {'format': 'json'})
        )
        response.raise_for_status()
        return response.json()

    def request_string(self, uri, qs_params=None):
        """Execute a REST call on the server and return string"""
        response = self._session.request(
            method='GET',
            uri=uri,
            qs_params=qs_params
        )
        response.raise_for_status()
        return response.text

    def request(self, uri, method, qs_params=None):
        """Execute a REST call on the server"""
        response = self._session.request(method=method,
                                         uri=uri,
                                         qs_params=qs_params)
        response.raise_for_status()
        return response
