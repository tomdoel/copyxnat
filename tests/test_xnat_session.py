# coding=utf-8

"""simplexnat tests"""

import pytest
import requests as requests
from mockito import mock, ANY, expect, verifyNoUnwantedInteractions
from requests.auth import HTTPBasicAuth

from copyxnat.config.server_params import XnatServerParams
from copyxnat.utils.error_utils import UserError

from copyxnat.xnat_backend.xnat_session import SessionId, RestWrapper, \
    XnatSession


@pytest.mark.usefixtures('unstub')
class TestXnatSession(object):

    @pytest.mark.parametrize("host, expected_host, expected_url", [('http://testhost.local', 'http://testhost.local', 'http://testhost.local/data/JSESSION')])
    @pytest.mark.parametrize("insecure, verify", [(True, False), (False, True)])
    def test_login_logout(self, host, expected_host, expected_url, insecure,
                          verify):
        server_params = XnatServerParams(host=host, user='fred',
                                         insecure=insecure)
        session = XnatSession(server_params)

        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=expected_host,
                                   success=True, verify=verify, cookie=cookie1):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

            # Second login should not trigger a rest call
            session.login()
            verifyNoUnwantedInteractions()

        # Logout
        with self._mock_auth_logout(expected_host=expected_host, success=True,
                                    verify=verify, cookie=cookie1):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Second logout should not trigger a rest call
            session.logout()
            verifyNoUnwantedInteractions()

        cookie2 = 'second_session_id'
        with self._mock_auth_login(expected_host=expected_host,
                                   success=True, verify=verify, cookie=cookie2):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

            # Second login should not trigger auth call
            session.login()
            verifyNoUnwantedInteractions()

        with self._mock_auth_logout(expected_host=expected_host, success=True,
                                    verify=verify, cookie=cookie2):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Logged out; expect no rest calls on session deletion
            session.__del__()
            verifyNoUnwantedInteractions()

    @pytest.mark.parametrize("host, expected_host", [('http://testhost.local', 'http://testhost.local')])
    def test_auto_logout(self, host, expected_host):
        server_params = XnatServerParams(host=host, user='fred')
        session = XnatSession(server_params)

        # Login
        cookie = 'first_session_id'
        with self._mock_auth_login(expected_host=expected_host,
                                   success=True, verify=True, cookie=cookie):
            session.login()
            verifyNoUnwantedInteractions()

        # Check auto logout on session deletion
        with self._mock_auth_logout(expected_host=expected_host,
                                    success=True, verify=True, cookie=cookie):
            session.__del__()
            verifyNoUnwantedInteractions()

    @pytest.mark.parametrize("host, expected_host, expected_url", [('http://testhost.local', 'http://testhost.local', 'http://testhost.local/data/JSESSION')])
    def test_no_auto_logout_if_already_logged_out(self, host,
                                                  expected_host,
                                                  expected_url):
        server_params = XnatServerParams(host=host, user='fred')
        session = XnatSession(server_params)
        cookie = 'second_session_id'

        with self._mock_auth_login(expected_host=expected_host,
                                   success=True, verify=True, cookie=cookie):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

        with self._mock_auth_logout(expected_host=expected_host,
                                    success=True, verify=True, cookie=cookie):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Check that session deletion does not trigger another logout
            session.__del__()
            verifyNoUnwantedInteractions()

    def _mock_auth_login(self, expected_host, success, verify, cookie):
        url = expected_host + '/data/JSESSION'
        return self._mock_response(
            method='post', url=url, success=success, verify=verify,
            auth=ANY(HTTPBasicAuth), response_text=cookie,
            expect_raise_for_status=success
        )

    def _mock_auth_logout(self, expected_host, success, verify, cookie):
        url = expected_host + '/data/JSESSION'
        return self._mock_response(
            method='delete', url=url, success=success, verify=verify,
            headers={'Cookie': 'JSESSIONID='+cookie},
            expect_raise_for_status=False
        )

    def _mock_request(self, method, url, success, verify, response_text,
                      headers, cookie, qs_params, body, stream,
                      expect_raise_for_status=True):
        headers_in = {} if not headers else headers.copy()
        headers_in['Cookie'] = 'JSESSIONID=' + cookie
        return self._mock_response(
            method=method, url=url, success=success, verify=verify,
            auth=None, response_text=response_text, headers=headers_in,
            expect_raise_for_status=expect_raise_for_status,
            params=qs_params, body=body, stream=stream
        )

    @staticmethod
    def _mock_response(method, url, success, verify, headers=None,
                       auth=None, response_text='OK', params=None,
                       expect_raise_for_status=False, body=None, stream=None):
        mock_args = {
            'status_code': 200 if success else 401,
            'text': response_text if success else 'TEST AUTH FAILURE RESPONSE',
        }

        if expect_raise_for_status:
            if success:
                mock_args['raise_for_status'] = lambda: None
            else:
                mock_args['raise_for_status'] = \
                    TestXnatSession._raise_for_status

        auth_response = mock(mock_args, spec=requests.Response)

        return expect(requests, times=1).request(
            url=url, method=method, auth=auth, headers=headers,
            params=params, data=body, verify=verify, stream=stream
        ).thenReturn(auth_response)

    @staticmethod
    def _raise_for_status():
        raise MockHttpError()

    @pytest.mark.parametrize("login_first", [True, False])
    @pytest.mark.parametrize("logout_last", [True, False])
    @pytest.mark.parametrize("insecure, expected_verify", [(True, False), (False, True)])
    def test_request(self, login_first, logout_last, insecure, expected_verify):

        # Setup
        host = 'http://test.server'
        params = XnatServerParams(host=host, user='fred', insecure=insecure)
        session = XnatSession(params)

        # First request
        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=host, success=True,
                                   verify=expected_verify, cookie=cookie1):
            if login_first:
                session.login()
                verifyNoUnwantedInteractions()

            api1 = 'my-api/call1'
            expected_url1 = host + '/' + api1
            self._do_request(session=session, cookie=cookie1,
                             api=api1,
                             expected_url=expected_url1,
                             expected_verify=expected_verify
                             )
            verifyNoUnwantedInteractions()

        # New request. Already logged in so do not expect login REST call
        api2 = 'my-api/call2'
        expected_url2 = host + '/' + api2
        self._do_request(session=session, cookie=cookie1,
                         api=api2,
                         expected_url=expected_url2,
                         expected_verify=expected_verify
                         )
        verifyNoUnwantedInteractions()

        # Logout
        with self._mock_auth_logout(expected_host=host, success=True,
                                    verify=expected_verify, cookie=cookie1):
            session.logout()
            verifyNoUnwantedInteractions()

        # New request will trigger a new login call
        cookie2 = 'second_session_id'
        with self._mock_auth_login(expected_host=host, success=True,
                                   verify=expected_verify, cookie=cookie2):
            api3 = 'my-api2/rest/call3'
            expected_url3 = host + '/' + api3
            self._do_request(session=session, cookie=cookie2, api=api3,
                             expected_url=host + '/' + api3,
                             expected_verify=expected_verify
                             )
            verifyNoUnwantedInteractions()

        # New request. Already logged in so do not expect login REST call
        api4 = 'my-api2/rest/call4'
        expected_url4 = host + '/' + api4
        self._do_request(session=session, cookie=cookie2, api=api4,
                         expected_url=expected_url4,
                         expected_verify=expected_verify
                         )
        verifyNoUnwantedInteractions()

        # Logout
        with self._mock_auth_logout(expected_host=host, success=True,
                                    verify=expected_verify, cookie=cookie2):
            if logout_last:
                session.logout()
                verifyNoUnwantedInteractions()

            # Check that session deletion does not trigger another logout
            session.__del__()
            verifyNoUnwantedInteractions()

    def test_reauth_success(self):
        # Tests when a REST call fails with authentication error, so
        # a new session is created and the REST call retries and succeeds

        host = 'http://test.server'
        params = XnatServerParams(host=host, user='fred', insecure=False)
        session = XnatSession(params)

        # First request
        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=host, success=True,
                                   verify=True, cookie=cookie1):
            api1 = 'my-api/call1'
            expected_url1 = host + '/' + api1
            self._do_request(session=session, cookie=cookie1,
                             api=api1,
                             expected_url=expected_url1,
                             expected_verify=True
                             )
            verifyNoUnwantedInteractions()

        # Trigger an authentication failure on new rest call but let reauth
        # succeed
        cookie2 = 'second_session_id'
        with self._mock_auth_login(
                expected_host=host, success=True, verify=True, cookie=cookie2
        ):
            api2 = 'my-api/call2'
            expected_url2 = host + '/' + api2
            self._do_request(session=session, cookie=cookie1, api=api2,
                             retry_cookie=cookie2,
                             expected_url=expected_url2, expected_verify=True,
                             success_first=False, success_second=True)

        # New session is valid so logout
        with self._mock_auth_logout(expected_host=host, success=True,
                                    verify=True, cookie=cookie2):
            session.__del__()
            verifyNoUnwantedInteractions()

    def test_reauth_failure(self):
        # Tests when a REST call fails with authentication error, try to create
        # a new session but this fails

        host = 'http://test.server'
        params = XnatServerParams(host=host, user='fred', insecure=False)
        session = XnatSession(params)

        # First request
        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=host, success=True,
                                   verify=True, cookie=cookie1):
            api1 = 'my-api/call1'
            expected_url1 = host + '/' + api1
            self._do_request(session=session, cookie=cookie1,
                             api=api1,
                             expected_url=expected_url1,
                             expected_verify=True
                             )
            verifyNoUnwantedInteractions()

        # Trigger an authentication failure on rest call, let the reauth fail
        cookie2 = 'fourth_session_id'
        with self._mock_auth_login(
                expected_host=host, success=False, verify=True, cookie=cookie2
        ):
            api2 = 'my-api/call2'
            expected_url2 = host + '/' + api2
            with pytest.raises(UserError) as e_info:
                self._do_request(session=session, cookie=cookie1, api=api2,
                                 retry_cookie=None,
                                 expected_url=expected_url2, expected_verify=True,
                                 success_first=False, success_second=False)

        # Should be no sessions remaining due to failure
        session.__del__()
        verifyNoUnwantedInteractions()

    def test_reauth_retry_failure(self):
        # This captures the case where user credentials succeed but the
        # subsequent REST call still returns an unauthorised error. In this
        # case a response is returned to the rest client rather than
        # raising an exception as it suggests some other access issue rather
        # than user credentials.

        host = 'http://test.server'
        params = XnatServerParams(host=host, user='fred', insecure=False)
        session = XnatSession(params)

        # First request
        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=host, success=True,
                                   verify=True, cookie=cookie1):
            api1 = 'my-api/call1'
            expected_url1 = host + '/' + api1
            self._do_request(session=session, cookie=cookie1,
                             api=api1,
                             expected_url=expected_url1,
                             expected_verify=True
                             )
            verifyNoUnwantedInteractions()

        # Trigger an authentication failure on rest call, let the reauth
        # succeed but make the request retry fail
        cookie2 = 'second_session_id'
        with self._mock_auth_login(
                expected_host=host, success=True, verify=True,
                cookie=cookie2
        ):
            api2 = 'my-api/call2'
            expected_url2 = host + '/' + api2

            with pytest.raises(MockHttpError) as e_info:
                self._do_request(session=session, cookie=cookie1, api=api2,
                             retry_cookie=cookie2,
                             expected_url=expected_url2,
                             expected_verify=True,
                             success_first=False, success_second=False)

    @pytest.mark.parametrize(
        "host, api, expected_host, expected_url", [
            ('http://test.server/', 'my-api/call', 'http://test.server', 'http://test.server/my-api/call'),
            ('http://test.server', 'my-api/call', 'http://test.server', 'http://test.server/my-api/call'),
            ('http://test.server/', '/my-api/call', 'http://test.server', 'http://test.server/my-api/call'),
            ('http://test.server/', 'my-api/call', 'http://test.server', 'http://test.server/my-api/call'),
            ('http://test.server/', 'my-api/call/', 'http://test.server', 'http://test.server/my-api/call/')
        ])
    @pytest.mark.parametrize("insecure, expected_verify", [(True, False), (False, True)])
    @pytest.mark.parametrize("stream", [True, False, None])
    def test_request_params(self, host, api, expected_host, expected_url, insecure,
                            expected_verify, stream):

        # Setup
        params = XnatServerParams(host=host, user='fred', insecure=insecure)
        session = XnatSession(params)

        # Request
        cookie1 = 'first_session_id'
        with self._mock_auth_login(expected_host=expected_host, success=True,
                                   verify=expected_verify, cookie=cookie1):
            self._do_request(session=session, cookie=cookie1, api=api,
                             expected_url=expected_url,
                             expected_verify=expected_verify,
                             stream=stream
                             )
            verifyNoUnwantedInteractions()

        # Deletion session to logout
        with self._mock_auth_logout(expected_host=expected_host, success=True,
                                    verify=expected_verify, cookie=cookie1):
            session.__del__()
            verifyNoUnwantedInteractions()

    def _do_request(
            self, session, cookie, expected_url, expected_verify,
            api=None, method=None, qs_params=None, body=None, headers=None,
            stream=None, success_first=True, success_second=True,
            retry_cookie=None
    ):
        # Set dummy parameters where not specified by the caller
        api = 'my-method' if api is None else api
        method = 'my-method' if method is None else method
        qs_params = {'song': 'yesterday', 'opera': 'carmen'} if \
            qs_params is None else qs_params
        body = 'ABCDEFG' if body is None else body
        headers = {'book': '1984', 'film': 'casablanca'} if \
            headers is None else headers
        stream = True if stream is None else stream
        dummy_response = 'OK'
        expected_response = dummy_response if success_first or success_second \
            else 'TEST AUTH FAILURE RESPONSE'

        with self._mock_request(
            method=method, url=expected_url, verify=expected_verify,
            qs_params=qs_params, body=body, headers=headers,
            response_text=dummy_response, stream=stream,
            success=success_first, cookie=cookie,
            expect_raise_for_status=success_first
        ):
            # If the first call fails then we expect the request to
            # reauthenticate and request again with a new session ID
            if retry_cookie:
                # Note: no with, so we must call verifyNoUnwantedInteractions()
                # later on
                self._mock_request(
                    method=method, url=expected_url, verify=expected_verify,
                    success=success_second, cookie=retry_cookie,
                    qs_params=qs_params, body=body, headers=headers,
                    response_text=dummy_response, stream=stream)

            assert session.request(
                method=method,
                uri=api,
                qs_params=qs_params,
                body=body,
                headers=headers,
                stream=stream
            ).text == expected_response

            # Important do verify here because the second mock request
            # expectation does not have a with
            verifyNoUnwantedInteractions()


@pytest.mark.usefixtures('unstub')
class TestRestWrapper(object):

    @pytest.mark.parametrize(
        "host, api, url", [
            ('http://test.server/', 'my-api/call', 'http://test.server/my-api/call'),
            ('http://test.server', 'my-api/call', 'http://test.server/my-api/call'),
            ('http://test.server/', '/my-api/call', 'http://test.server/my-api/call'),
            ('http://test.server/', 'my-api/call', 'http://test.server/my-api/call'),
            ('http://test.server/', 'my-api/call/', 'http://test.server/my-api/call/')
        ])
    def test_get_url(self, host, api, url):
        server_params = XnatServerParams(host=host, user='fred', insecure=False)
        rest_wrapper = RestWrapper(server_params)
        assert rest_wrapper.get_url(api) == url


class MockHttpError(Exception):
    pass


class TestSessionId(object):

    def test_exists_reset(self):
        session_id = SessionId()

        assert not session_id.exists()
        session_id.set('abcde')
        assert session_id.exists()
        session_id.reset()
        assert not session_id.exists()

    def test_session_header(self):
        session_id = SessionId()

        with pytest.raises(Exception) as e_info:
            session_id.session_header('')

        with pytest.raises(Exception) as e_info:
            session_id.set('')

        session_id.set('abcde')
        assert session_id.session_header() == {'Cookie': 'JSESSIONID=abcde'}

        session_id.set('fghij')
        assert session_id.session_header() == {'Cookie': 'JSESSIONID=fghij'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.session_header()

        session_id.set('hijkl')
        assert session_id.session_header() == {'Cookie': 'JSESSIONID=hijkl'}

    def test_fails_for_empty_id(self):
        session_id = SessionId()

        with pytest.raises(Exception) as e_info:
            session_id.session_header()

        with pytest.raises(Exception) as e_info:
            session_id.set('')

        session_id.set('abcde')
        assert session_id.session_header() == {'Cookie': 'JSESSIONID=abcde'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.session_header()
