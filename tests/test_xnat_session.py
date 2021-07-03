# coding=utf-8

"""simplexnat tests"""

import pytest
import requests as requests
from mockito import when, mock

from copyxnat.config.server_params import XnatServerParams

from copyxnat.xnat_backend.xnat_session import SessionId, RestWrapper


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


class TestSession(object):

    def test_exists_reset(self):
        session_id = SessionId()

        assert not session_id.exists()
        session_id.set('abcde')
        assert session_id.exists()
        session_id.reset()
        assert not session_id.exists()

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
