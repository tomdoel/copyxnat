# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""
import requests
from requests.auth import HTTPBasicAuth

from copyxnat.xnat_backend.utis import Utils


class XnatSession(object):
    """
    Wrapper around the XNAT REST API which automatically handles session
    authentication and tokens using the provided credentials
    """

    def __init__(self, params):
        self._params = params
        self._rest = RestWrapper(params=params)
        self._session_id = SessionId()
        self._verify = not params.insecure

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
                return response

    def login(self):
        """Create this XNAT session if it does not already exist"""

        if not self._session_id.exists():
            response = self._request(
                method='post',
                uri='JSESSION',
                auth=HTTPBasicAuth(self._params.user, self._params.pwd)
            )
            response.raise_for_status()
            self._session_id.set(response.text)

    def logout(self):
        """End this XNAT session"""

        if self._session_id.exists():
            self._request(
                method='delete',
                uri='JSESSION',
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
        self._session_id = new_id

    def reset(self):
        """Indicate the current session IF is no longer valid"""
        self._session_id = None

    def session_header(self):
        """Return XNAT session ID header for REST authentication"""
        if not self._session_id:
            raise ValueError('No session cookie present')
        return {'Cookie': 'JSESSIONID={}'.format(self._session_id)}

    def add_session_header(self, headers=None):
        """Return dictionary of REST headers which includes any specified
        headers and adds a cookie header containing the Session ID"""
        if not self._session_id:
            raise ValueError('No session cookie present')
        rest_headers = headers if headers is not None else {}
        rest_headers['Cookie'] = 'JSESSIONID={}'.format(self._session_id)
        return rest_headers


class RestWrapper(object):
    """
    Wrapper around the XNAT REST API which automatically assembles the URL
    from the server name in the provided params and REST API URI
    """
    def __init__(self, params):
        self._host = params.host.strip()
        self._verify = not params.insecure

    def request(self, method, uri, qs_params=None, body=None, headers=None,
                auth=None, stream=None):
        """
        Send a REST call to an XNAT server. The URL of the call will be
        assembled from the server host and the URI

        :param method: Request method (eg get, put, post)
        :param uri: XNAT REST API string (excluding https://server/data/)
        :param qs_params: dictionary of querystring parameters for the request
        :param body: request body
        :param headers: dictionary of headers for the request
        :param auth: Authentication object for the requests library
        :param stream: True if content is streamed
        :return: requests.Response
        """
        return requests.request(
            method=method,
            url=self.get_url(uri),
            auth=auth,
            params=qs_params,
            headers=headers,
            data=body,
            verify=self._verify,
            stream=stream
        )

    def get_url(self, uri):
        """Return full REST URL for the given URI"""
        return '{}/data/{}'.format(self._host.rstrip('/'), uri.lstrip('/'))
