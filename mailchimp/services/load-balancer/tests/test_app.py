import requests
import sys
import os
import enum
import sys
if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
    from unittest import mock
else:
    import mock

service_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(service_path)
from load-balancer.app import app

parent_path = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper
helper = helper.Helper("mailchimp")


class MockFailure(enum.Enum):
    SUCCESS = 0
    APP_SERVER_FAIL = 1
    APP_SERVER_TIMEOUT = 2
    APP_SERVER_ERROR = 3
    APP_SERVER_UNAVAILABLE = 4


class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data


def mock_requests_get_with_failure_setting(failure_setting):
    def mock_requests_get(*args, **kwargs):
        app_server_request = "http://{}:{}/urls/prettyurl".format(helper.resolve_requests_host('app-server'), helper.get_port('app-server'))
        if args == (app_server_request,):
            if failure_setting == MockFailure.APP_SERVER_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.APP_SERVER_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.APP_SERVER_ERROR:
                MockResponse({}, 500)
            elif failure_setting == MockFailure.APP_SERVER_UNAVAILABLE:
                MockResponse({}, 503)
            else:
                return MockResponse(RESPONSE, 200)

    return mock_requests_get


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_lb_success(mock_get):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.APP_SERVER_FAIL))
def test_lb_app_server_fail(mock_get):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.APP_SERVER_TIMEOUT))
def test_lb_app_server_timeout(mock_get):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 503


RESPONSE = {
    "result": "internalurl"
}
