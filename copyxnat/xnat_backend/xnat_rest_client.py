# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import os

from copyxnat.xnat_backend.utis import Utils
from copyxnat.xnat_backend.xnat_session import XnatSession


class XnatRestClient(object):
    """Wrapper around XNAT REST API"""

    def __init__(self, params):
        self._session = XnatSession(params)

    def __del__(self):
        self.logout()

    def datatype(self, uri):
        """Return the XNAT datatype of this item"""
        response = self._session.request(
            method='GET',
            uri=uri,
            qs_params={'format': 'json'}
        )
        response.raise_for_status()
        datatype = response.json().get('items')[0].get('meta').get('xsi:type')
        return datatype

    def items(self, uri, name, optional=False):
        """
        Return list of items for this server.
        optional should be True if not mandated by the schema
        """
        extended_uri = '{}/{}'.format(uri, name)
        return self.request_json_property(extended_uri, optional=optional)

    def file_attributes(self, parent_uri, label):
        """Return standard attributes for this file"""
        items = self.request_json_property(
        return items[0]
            uri='{}/files'.format(parent_uri),
            qs_params={'Name': label}
        )

    def resource_attributes(self, parent_uri, label):
        """Return standard attributes for this resource"""
        items = self.request_json_property(
        return items[0]
            uri='{}/resources'.format(parent_uri),
            qs_params={'xnat_abstractresource_id': label}
        )

    def experiment_list(self, project):
        """Return list of experiments in this project"""
        exps = self.request_json_property(
            'projects/{}/experiments'.format(project))
        return [exp['label'] for exp in exps]

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(self.request_json_property(
            'projects/{}/experiments'.format(project)))

    def logout(self):
        """Return XML representation of this XNAT item"""

        self._session.logout()

    def datatypes(self):
        """Return list of XNAT datatype names present on server"""

        return [element['ELEMENT_NAME'] for element in
                self.request_json_property('/search/elements')]

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

    def create_resource_folder(self, uri, resource_format, tags, content):
        """
        Create a XNAT resource folder

        :param uri: Relative URI
        :param resource_format: XNAT format attribute
        :param tags:  XNAT tags attribute
        :param content: XNAT content attribute
        """
        optional_params = self._optional_params({'format': resource_format,
                                                 'tags': tags,
                                                 'content': content})
        response = self._session.request(uri=uri, method='PUT',
                                         qs_params=optional_params)
        response.raise_for_status()

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
        qs_params = self._optional_params({'format': file_format,
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

    def request_json_property(self, uri, optional=False, qs_params=None):
        """Execute a REST call on the server and return result as list

        If optional is True, then a 404 response will yield an empty list"""
        response = self._session.request(
            method='GET',
            uri=uri,
            qs_params=Utils.combine_dicts(qs_params, {'format': 'json'})
        )
        if optional and response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()["ResultSet"]['Result']

    def request_string(self, uri):
        """Execute a REST call on the server and return string"""

        response = self._session.request(method='GET', uri=uri)
        response.raise_for_status()
        return response.text

    def request_xml_string(self, uri):
        """Return XML representation of this XNAT item"""

        response = self._session.request(method='GET', uri=uri,
                                         qs_params={'format': 'xml'})
        response.raise_for_status()
        return response.text

    def request(self, uri, method, qs_params=None):
        """Execute a REST call on the server"""
        response = self._session.request(method=method,
                                         uri=uri,
                                         qs_params=qs_params)
        response.raise_for_status()
        return response

    @staticmethod
    def _optional_params(params):
        optional_params = {}
        for key, value in params.items():
            if value is not None:
                optional_params[key] = value
        return optional_params
