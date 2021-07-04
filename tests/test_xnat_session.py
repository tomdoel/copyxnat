# coding=utf-8

"""simplexnat tests"""

import pytest
import requests as requests
from mockito import when, mock, ANY, expect, verifyNoUnwantedInteractions
from requests.auth import HTTPBasicAuth

from copyxnat.config.server_params import XnatServerParams

from copyxnat.xnat_backend.xnat_session import SessionId, RestWrapper, \
    XnatSession


@pytest.mark.usefixtures('unstub')
class TestXnatSession(object):

    @pytest.mark.parametrize("host, url", [('http://testhost.local', 'http://testhost.local/data/JSESSION')])
    @pytest.mark.parametrize("insecure, verify", [(True, False), (False, True)])
    def test_login_logout(self, host, url, insecure, verify):
        server_params = XnatServerParams(host=host,
                                         user='fred',
                                         insecure=insecure)
        session = XnatSession(server_params)

        cookie1 = 'first_session_id'
        with self._mock_auth_login(url=url, success=True, verify=verify,
                                   cookie=cookie1):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

            # Second login should not trigger a rest call
            session.login()
            verifyNoUnwantedInteractions()

        # Logout
        with self._mock_auth_logout(url=url, success=True, verify=verify,
                                    cookie=cookie1):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Second logout should not trigger a rest call
            session.logout()
            verifyNoUnwantedInteractions()

        cookie2 = 'second_session_id'
        with self._mock_auth_login(url=url, success=True, verify=verify,
                                   cookie=cookie2):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

            # Second login should not trigger auth call
            session.login()
            verifyNoUnwantedInteractions()

        with self._mock_auth_logout(url=url, success=True, verify=verify,
                                    cookie=cookie2):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Logged out; expect no rest calls on session deletion
            session.__del__()
            verifyNoUnwantedInteractions()

    @pytest.mark.parametrize("host, url", [('http://testhost.local', 'http://testhost.local/data/JSESSION')])
    def test_auto_logout(self, host, url):
        server_params = XnatServerParams(host=host, user='fred')
        session = XnatSession(server_params)

        # Login
        cookie = 'first_session_id'
        with self._mock_auth_login(url=url, success=True, verify=True,
                                   cookie=cookie):
            session.login()
            verifyNoUnwantedInteractions()

        # Check auto logout on session deletion
        with self._mock_auth_logout(url=url, success=True, verify=True,
                                    cookie=cookie):
            session.__del__()
            verifyNoUnwantedInteractions()

    @pytest.mark.parametrize("host, url", [('http://testhost.local', 'http://testhost.local/data/JSESSION')])
    def test_no_auto_logout_if_already_logged_out(self, host, url):
        server_params = XnatServerParams(host=host, user='fred')
        session = XnatSession(server_params)
        cookie = 'second_session_id'

        with self._mock_auth_login(url=url, success=True, verify=True,
                                   cookie=cookie):
            # Login
            session.login()
            verifyNoUnwantedInteractions()

        with self._mock_auth_logout(url=url, success=True, verify=True,
                                    cookie=cookie):
            # Logout
            session.logout()
            verifyNoUnwantedInteractions()

            # Check that session deletion does not trigger another logout
            session.__del__()
            verifyNoUnwantedInteractions()

    def _mock_auth_login(self, url, success, verify, cookie):
        return self._mock_response(
            method='post', url=url, success=success, verify=verify,
            auth=ANY(HTTPBasicAuth), response_text=cookie,
            expect_raise_for_status=True
        )

    def _mock_auth_logout(self, url, success, verify, cookie):
        return self._mock_response(
            method='delete', url=url, success=success, verify=verify,
            headers={'Cookie': 'JSESSIONID='+cookie},
            expect_raise_for_status=False
        )

    @staticmethod
    def _mock_response(method, url, success, verify, headers=None,
                       auth=None, response_text='OK',
                       expect_raise_for_status=False):
        mock_args = {
            'status_code': 200,
            'text': response_text,
        }
        if expect_raise_for_status:
            mock_args['raise_for_status'] = lambda: None

        auth_response = mock(mock_args, spec=requests.Response)

        return expect(requests, times=1).request(
            url=url, method=method, auth=auth, headers=headers,
            params=None, data=None, verify=verify, stream=None
        ).thenReturn(auth_response)



@pytest.mark.usefixtures('unstub')
class TestRestWrapper(object):

    @pytest.mark.parametrize(
        "host, api, url", [
            ('http://test.server/', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', '/my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', 'my-api/call/', 'http://test.server/data/my-api/call/')
        ])
    def test_get_url(self, host, api, url):
        server_params = XnatServerParams(host=host, user='fred', insecure=False)
        rest_wrapper = RestWrapper(server_params)
        assert rest_wrapper.get_url(api) == url

    @pytest.mark.parametrize(
        "host, api, url", [
            ('http://test.server/', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', '/my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', 'my-api/call', 'http://test.server/data/my-api/call'),
            ('http://test.server/', 'my-api/call/', 'http://test.server/data/my-api/call/')
        ])
    @pytest.mark.parametrize("insecure, verify", [(True, False), (False, True)])
    @pytest.mark.parametrize("stream", [True, False, None])
    def test_rest_wrapper(self, host, api, url, insecure, verify, stream):
        server_params = XnatServerParams(host=host,
                                         user='fred',
                                         insecure=insecure)

        # These parameters are passed through so just check they are unaltered
        dummy_method = 'my-method'
        dummy_qs_params = {'first': 'value1', 'second': 'value2'}
        dummy_headers = {'hfirst': 'hvalue1', 'hsecond': 'hvalue2'}
        dummy_body = 'ABCDEFG'
        dummy_auth = object()

        response = mock({
            'status_code': 200,
            'text': 'OK'
        }, spec=requests.Response)

        rest_wrapper = RestWrapper(server_params)

        when(requests).request(
            url=url,
            method=dummy_method,
            auth=dummy_auth,
            params=dummy_qs_params,
            headers=dummy_headers,
            data=dummy_body,
            verify=verify,
            stream=stream
        ).thenReturn(response)

        actual_response = rest_wrapper.request(
            method=dummy_method,
            uri=api,
            qs_params=dummy_qs_params,
            body=dummy_body,
            headers=dummy_headers,
            auth=dummy_auth,
            stream=stream
        )
        assert actual_response == response


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
            session_id.add_session_header()

        session_id.set('abcde')
        assert session_id.session_header() == {'Cookie': 'JSESSIONID=abcde'}
        session_id.set('fghij')
        assert session_id.add_session_header() == {'Cookie': 'JSESSIONID=fghij'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()

    def test_add_session_header(self):
        session_id = SessionId()

        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()

        session_id.set('abcde')
        assert session_id.add_session_header() == {'Cookie': 'JSESSIONID=abcde'}
        assert session_id.add_session_header({'book': '1984', 'film': 'casablanca'}) == {'Cookie': 'JSESSIONID=abcde', 'book': '1984', 'film': 'casablanca'}
        session_id.set('fghij')
        assert session_id.add_session_header() == {'Cookie': 'JSESSIONID=fghij'}
        assert session_id.add_session_header({'book': '1984', 'film': 'casablanca'}) == {'Cookie': 'JSESSIONID=fghij', 'book': '1984', 'film': 'casablanca'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()

    def test_fails_for_empty_id(self):
        session_id = SessionId()

        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()

        session_id.set('abcde')
        assert session_id.add_session_header() == {'Cookie': 'JSESSIONID=abcde'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()

        session_id.set('fghij')
        assert session_id.add_session_header() == {'Cookie': 'JSESSIONID=fghij'}

        session_id.reset()
        with pytest.raises(Exception) as e_info:
            session_id.add_session_header()
