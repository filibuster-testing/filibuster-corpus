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
from app-server.app import app

parent_path = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper
helper = helper.Helper("mailchimp")


class MockFailure(enum.Enum):
    SUCCESS = 0
    REQUESTMAPPER_FAIL = 1
    REQUESTMAPPER_TIMEOUT = 2
    DB_PRIMARY_FAIL = 3
    DB_PRIMARY_TIMEOUT = 4
    DB_PRIMARY_READ_ONLY = 5 
    DB_PRIMARY_FAIL_DB_SECONDARY_FAIL = 6
    DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT = 7
    DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY = 8


class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data


def mock_requests_get_with_failure_setting(failure_setting):
    def mock_requests_get(*args, **kwargs):
        requestmapper_request = "http://{}:{}/urls/prettyurl".format(helper.resolve_requests_host('requestmapper'), helper.get_port('requestmapper'))
        if args == (requestmapper_request,):
            if failure_setting == MockFailure.REQUESTMAPPER_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.REQUESTMAPPER_TIMEOUT:
                raise requests.exceptions.Timeout
            else:
                return MockResponse(RESPONSE, 200)

        db_primary_request = "http://{}:{}/read".format(helper.resolve_requests_host('db-primary'), helper.get_port('db-primary'))
        if args == (db_primary_request,):
            if failure_setting in [MockFailure.DB_PRIMARY_FAIL, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY]:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.DB_PRIMARY_TIMEOUT:
                raise requests.exceptions.Timeout
            else:
                return MockResponse({}, 200)
        
        db_secondary_request = "http://{}:{}/read".format(helper.resolve_requests_host('db-secondary'), helper.get_port('db-secondary'))
        if args == (db_secondary_request,):
            if failure_setting == MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT:
                raise requests.exceptions.Timeout
            else:
                return MockResponse({}, 200)

    return mock_requests_get


def mock_requests_post_with_failure_setting(failure_setting):
    def mock_requests_post(*args, **kwargs):
        # db_primary_request = "http://{}:{}/write/urls/prettyurl".format(helper.resolve_requests_host('db-primary'), helper.get_port('db-primary'))
        db_primary_request = "http://0.0.0.0:5003/write/urls/prettyurl"
        if args == (db_primary_request,):
            if failure_setting in [MockFailure.DB_PRIMARY_FAIL, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT, MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY]:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.DB_PRIMARY_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.DB_PRIMARY_READ_ONLY:
                return MockResponse({}, 403)
            else:
                return MockResponse({}, 200)

        db_secondary_request = "http://{}:{}/write/urls/prettyurl".format(helper.resolve_requests_host('db-secondary'), helper.get_port('db-secondary'))
        if args == (db_secondary_request,):
            if failure_setting == MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY:
                return MockResponse({}, 403)
            else:
                return MockResponse({}, 200)

    return mock_requests_post


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_app_server_success(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REQUESTMAPPER_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_app_server_requestmapper_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 500


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REQUESTMAPPER_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_app_server_requestmapper_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 500


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_FAIL))
def test_app_server_db_primary_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_TIMEOUT))
def test_app_server_db_primary_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_READ_ONLY))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_READ_ONLY))
def test_app_server_db_primary_read_only(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json["result"] == RESPONSE["result"]
    assert reply.json["alert"] == ALERT


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_FAIL))
def test_app_server_db_primary_fail_db_secondary_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 500


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_TIMEOUT))
def test_app_server_db_primary_fail_db_secondary_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 500


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.DB_PRIMARY_FAIL_DB_SECONDARY_READ_ONLY))
def test_app_server_db_primary_fail_db_secondary_read_only(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/urls/prettyurl") 
    assert reply.status_code == 200
    assert reply.json["result"] == RESPONSE["result"]
    assert reply.json["alert"] == ALERT


RESPONSE = {
    "result": "internalurl"
}

ALERT = "cannot write to DB"
