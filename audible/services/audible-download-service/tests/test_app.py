import requests
import sys
import os
import enum
import sys
if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from audible-download-service.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("audible")

class MockFailure(enum.Enum): 
  SUCCESS = 0
  OWNERSHIP_FAIL = 1
  OWNERSHIP_TIMEOUT = 2
  OWNERSHIP_NOT_FOUND = 3
  OWNERSHIP_FORBIDDEN = 4
  ACTIVATION_FAIL = 5
  ACTIVATION_TIMEOUT = 6
  STATS_FAIL = 7
  STATS_TIMEOUT = 8

class MockResponse:
    def __init__(self, json_data, status_code):
      self.json_data = json_data
      self.status_code = status_code

    def json(self):
      return self.json_data

def mock_requests_get_with_failure_setting(failure_setting):
  def mock_requests_get(*args, **kwargs):
    ownership_request = "{}/users/user1/books/book2".format(helper.get_service_url("ownership"))
    if args == (ownership_request,):
      if failure_setting == MockFailure.OWNERSHIP_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.OWNERSHIP_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.OWNERSHIP_NOT_FOUND:
        status_code = 404
      elif failure_setting == MockFailure.OWNERSHIP_FORBIDDEN:
        status_code = 403
      else:
        status_code = 200
      return MockResponse({}, status_code)

    activation_request = "{}/books/book2".format(helper.get_service_url("activation"))
    if args == (activation_request,):
      if failure_setting == MockFailure.ACTIVATION_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.ACTIVATION_TIMEOUT:
        raise requests.exceptions.Timeout
      return MockResponse(ACTIVATION_RESPONSE, 200)
  return mock_requests_get

def mock_requests_post_with_failure_setting(failure_setting):
  def mock_requests_post(*args, **kwargs):
    ownership_request = "{}/users/user1/books/book2".format(helper.get_service_url("ownership"))
    if args == (ownership_request,):
      if failure_setting == MockFailure.STATS_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.STATS_TIMEOUT:
        raise requests.exceptions.Timeout
      else:
        status_code = 201
      return MockResponse({}, status_code)
  return mock_requests_post


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_success(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 200
  assert reply.json == ACTIVATION_RESPONSE

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.OWNERSHIP_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_ownership_fail(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.OWNERSHIP_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_ownership_timeout(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.OWNERSHIP_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_ownership_not_found(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.OWNERSHIP_FORBIDDEN))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_ownership_forbidden(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 403

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ACTIVATION_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_activation_fail(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ACTIVATION_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_ads_activation_timeout(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503


# Expect program to return normally in cases of failure of the Stats service

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.STATS_FAIL))
def test_ads_stats_fail(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 200

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.STATS_TIMEOUT))
def test_ads_stats_timeout(mock_get, mock_post):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 200


ACTIVATION_RESPONSE = {
    "license": "745c723e03084d27553fb9d4037b08c1"
}
