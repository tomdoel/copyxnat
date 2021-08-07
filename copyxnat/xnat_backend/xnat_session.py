# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import requests
from requests.auth import HTTPBasicAuth
from six import raise_from

from copyxnat.utils.error_utils import UserError
from copyxnat.xnat_backend.utis import Utils


class XnatSession(object):
    """
    Wrapper around the XNAT REST API which automatically handles session
    authentication and tokens using the provided credentials
    """

    def __init__(self, params, read_only=False):
        self._params = params
        self._rest = RestWrapper(params=params)
        self._session_id = SessionId()
        self._verify = not params.insecure
        self._read_only = read_only

    def __del__(self):
        self.logout()

    def request(self, method, uri, qs_params=None, body=None, headers=None,
                stream=None):
        """
        Send a REST call to an XNAT server. The call will be authenticated
        automatically by adding the XNAT JSESSION ID to the REST headers. If
        the JSESSION ID does not already exist, it will be created by
        authenticating with the server using the user credentials.

        :param method: Request method (eg get, put, post)
        :param uri: XNAT REST API string (excluding https://server/data/)
        :param qs_params: dictionary of querystring parameters for the request
        :param body: request body
        :param headers: dictionary of headers for the request
        :param stream: True if content is streamed
        :return: requests.Response
        """

        if self._read_only and method.lower() in ('delete', 'post', 'put'):
            msg = 'Programming error: {} request not permitted in read-only ' \
                  'mode: {}'.format(method.upper(), uri)
            raise RuntimeError(msg)

        while True:
            # If using an existing session, reauthentication is permitted
            # because the existing session may have expired
            permit_auth_retry = self._session_id.exists()

            # Create session if it does not yet exist
            self.login()

            response = self._request(
                method=method,
                uri=uri,
                qs_params=qs_params,
                headers=Utils.combine_dicts(headers,
                                            self._session_id.session_header()),
                body=body,
                stream=stream
            )

            if permit_auth_retry and response.status_code == 401:
                # Authentication failed. The session cookie may have expired,
                # so invalidate and retry to trigger a new session
                self._session_id.reset()
            else:
                response.raise_for_status()
                return response

    def login(self):
        """Create this XNAT session if it does not already exist"""

        if not self._session_id.exists():
            try:
                response = self._request(
                    method='post',
                    uri='data/JSESSION',
                    auth=HTTPBasicAuth(self._params.user, self._params.pwd)
                )
            except requests.exceptions.SSLError as exc:
                raise_from(UserError(
                    'SSL error on server {}. This can occur if the server '
                    'certificate has expired or is self-signed. For testing '
                    'you can use insecure mode -k to bypass SSL verification.'.
                        format(self._params.host), cause=exc), exc)

            except requests.exceptions.ConnectionError as exc:
                raise_from(UserError(
                    'Cannot connect to server {}. Please check the URL is '
                    'correct and the server is running.'.format(
                        self._params.host), cause=exc), exc)

            if response.status_code == 401:
                raise UserError('Incorrect password for {}@{}'.format(
                    self._params.user, self._params.host
                ))
            response.raise_for_status()
            self._session_id.set(response.text)

    def logout(self):
        """End this XNAT session"""

        if self._session_id.exists():
            self._request(
                method='delete',
                uri='data/JSESSION',
                headers=self._session_id.session_header()
            )
            self._session_id.reset()

    def _request(self, method, uri, qs_params=None, body=None, headers=None,
                 auth=None, stream=None):
        return requests.request(
            method=method,
            url=self._rest.get_url(uri),
            auth=auth,
            params=qs_params,
            headers=headers,
            data=body,
            verify=self._verify,
            stream=stream
        )


class SessionId(object):
    """Wrapper around an XNAT session ID cookie"""

    def __init__(self):
        self._session_id = None

    def exists(self):
        """Return True if there is an existing session ID"""
        return self._session_id is not None

    def set(self, new_id):
        """Set a new session ID"""
        if not new_id:
            raise ValueError('No session ID specified')
        self._session_id = new_id

    def reset(self):
        """Indicate the current session IF is no longer valid"""
        self._session_id = None

    def session_header(self):
        """Return XNAT session ID header for REST authentication"""
        if not self._session_id:
            raise ValueError('No session cookie present')
        return {'Cookie': 'JSESSIONID={}'.format(self._session_id)}


class RestWrapper(object):
    """
    Wrapper around the XNAT REST API which automatically assembles the URL
    from the server name in the provided params and REST API URI
    """
    def __init__(self, params):
        self._host = params.host.strip()
        self._verify = not params.insecure

    def get_url(self, uri):
        """Return full REST URL for the given URI"""
        return '{}/{}'.format(self._host.rstrip('/'), uri.lstrip('/'))
