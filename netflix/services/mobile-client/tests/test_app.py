import sys
import os
import requests
import enum

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
    from unittest import mock
else:
    import mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from mobile-client.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("netflix")

class MockFailure(enum.Enum):
    SUCCESS = 0
    API_GATEWAY_FAIL = 1 
    API_GATEWAY_TIMEOUT = 2
    API_GATEWAY_NOT_FOUND = 3

class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


def mock_requests_get_with_failure_setting(failure_setting):
    def mock_requests_get(*args, **kwargs):
        api_gateway_request = "{}/homepage/users/chris_rivers".format(helper.get_service_url("api-gateway"))
        if args == (api_gateway_request,):
            if failure_setting == MockFailure.API_GATEWAY_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.API_GATEWAY_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.API_GATEWAY_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(RESPONSE, status_code)
    
    return mock_requests_get


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_client_success(mock_get):
    client = app.test_client()
    reply = client.get("/netflix/homepage/users/chris_rivers")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.API_GATEWAY_FAIL))
def test_client_api_gateway_fail(mock_get):
    client = app.test_client()
    reply = client.get("/netflix/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.API_GATEWAY_TIMEOUT))
def test_client_api_gateway_timeout(mock_get):
    client = app.test_client()
    reply = client.get("/netflix/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.API_GATEWAY_NOT_FOUND))
def test_client_api_gateway_not_found(mock_get):
    client = app.test_client()
    reply = client.get("/netflix/homepage/users/chris_rivers")
    assert reply.status_code == 404


RESPONSE = {
    "key": "value"
}
