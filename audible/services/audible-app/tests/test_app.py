import requests
import sys
import os
import enum

import sys
if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from audible-app.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("audible")

class MockFailure(enum.Enum):
  SUCCESS = 0
  CDE_FAIL = 1
  CDE_TIMEOUT = 2
  CDE_NOT_FOUND = 3
  CDS_FAIL = 4
  CDS_TIMEOUT = 5
  CDS_NOT_FOUND = 6
  CDS_FORBIDDEN = 7
  CDS_SERVICE_UNAVAILABLE = 8
  CDS_INTERNAL_SERVER_ERROR = 9

class MockResponse:
    def __init__(self, data, status_code):
      self.data = data
      self.content = data
      self.status_code = status_code

    def json(self):
      return self.data

def mock_requests_get_with_failure_setting(failure_setting):
  def mock_requests_get(*args, **kwargs):
    cde_request = "{}/users/user1/books/book2".format(helper.get_service_url("content-delivery-engine"))
    if args == (cde_request,):
      if failure_setting == MockFailure.CDE_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.CDE_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.CDE_NOT_FOUND:
        status_code = 404
      else:
        status_code = 200
      return MockResponse(CDE_RESPONSE, status_code)

    metadata_request = CDE_RESPONSE["url"]
    if args == (metadata_request,):
      if failure_setting == MockFailure.CDS_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.CDS_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.CDS_NOT_FOUND:
        status_code = 404
      elif failure_setting == MockFailure.CDS_FORBIDDEN:
        status_code = 403
      elif failure_setting == MockFailure.CDS_SERVICE_UNAVAILABLE:
        status_code = 503
      elif failure_setting == MockFailure.CDS_INTERNAL_SERVER_ERROR:
        status_code = 500
      else:
        status_code = 200
      return MockResponse(CDS_RESPONSE, status_code)

  return mock_requests_get


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_audible_success(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 200
  assert reply.data == CDS_RESPONSE

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDE_FAIL))
def test_audible_cde_fail(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDE_TIMEOUT))
def test_audible_cde_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDE_NOT_FOUND))
def test_audible_cde_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDS_FAIL))
def test_audible_cds_fail(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDS_TIMEOUT))
def test_audible_cds_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDS_FORBIDDEN))
def test_audible_cds_forbidden(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 403

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDS_SERVICE_UNAVAILABLE))
def test_audible_cds_service_unavailable(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.CDS_INTERNAL_SERVER_ERROR))
def test_audible_cds_internal_server_error(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503



CDE_RESPONSE = {
    "url": "http://0.0.0.0:5002/users/user1/books/book2"
}

CDS_RESPONSE = b"This is book 2."
