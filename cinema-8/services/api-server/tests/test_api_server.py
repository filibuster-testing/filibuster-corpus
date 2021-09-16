import time
import pytest
import requests
import threading
import json

from multiprocessing import Process
import sys
import os
import enum

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

from api-server.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("cinema-8")

class MockFailure(enum.Enum): 
  SUCCESS = 0
  FAIL_MONOLITH = 1
  MONOLITH_TIMEOUT = 2
  MONOLITH_NOT_FOUND = 3

def mock_requests_get_with_failure_setting(failure_setting):
  class MockResponse:
    def __init__(self, json_data, status_code):
      self.json_data = json_data
      self.status_code = status_code

    def json(self):
      return self.json_data

  success_status_code = 200
  def mock_requests_get(*args, **kwargs):
    bookings_request = "http://{}:{}/users/chris_rivers/bookings".format(helper.resolve_requests_host('monolith'), helper.get_port('monolith'))
    if (args == (bookings_request,)):
      if (failure_setting == MockFailure.FAIL_MONOLITH):
        raise requests.exceptions.ConnectionError
      if (failure_setting == MockFailure.MONOLITH_TIMEOUT):
        raise requests.exceptions.Timeout
      status_code = 404 if failure_setting == MockFailure.MONOLITH_NOT_FOUND else success_status_code
      return MockResponse(GOOD_RESPONSE, status_code)
  return mock_requests_get



@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_cinema_8_api_server_success(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":8.8,"title":"Creed","uri":"/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"}]}\n'
    
@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_MONOLITH))
def test_cinema_8_api_server_fail_monolith(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MONOLITH_TIMEOUT))
def test_cinema_8_api_server_monolith_timeout(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MONOLITH_NOT_FOUND))
def test_cinema_8_api_server_monolith_not_found(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.status_code == 404

GOOD_RESPONSE = {
    "20151201": [{
        "rating": 8.8,
        "title": "Creed",
        "uri": "/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    }]
}
