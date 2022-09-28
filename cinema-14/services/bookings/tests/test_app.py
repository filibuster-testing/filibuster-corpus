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

from bookings.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("cinema-14")

with open("{}/cinema-14/services/movies/movies.json".format(os.path.dirname(parent_path)), "r") as f:
    movies = json.load(f)

class MockFailure(enum.Enum): 
  SUCCESS = 0
  FAIL_MOVIES = 1
  MOVIES_TIMEOUT = 2

def mock_requests_get_with_failure_setting(failure_setting):
  class MockResponse:
    def __init__(self, json_data, status_code):
      self.json_data = json_data
      self.status_code = status_code

    def json(self):
      return self.json_data

  success_status_code = 200
  def mock_requests_get(*args, **kwargs):
    movies_request = "http://{}:{}/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6".format(helper.resolve_requests_host('movies'), helper.get_port('movies'))
    if (args == (movies_request,)):
      if (failure_setting == MockFailure.FAIL_MOVIES):
        raise requests.exceptions.ConnectionError
      if (failure_setting == MockFailure.MOVIES_TIMEOUT):
        raise requests.exceptions.Timeout
      movieid = '267eedb8-0f5d-42d5-8f43-72426b9fb3e6'
      result = movies[movieid]
      result["uri"] = "/movies/{}".format(movieid)
      return MockResponse(result, success_status_code)

  return mock_requests_get

def test_cinema_14_booking_records_index():
    client = app.test_client()
    reply = client.get("/")
    actual_reply = reply.json
    assert reply.status_code == 200

def test_cinema_14_booking_records_users():
    client = app.test_client()
    reply = client.get("/bookings")
    actual_reply = reply.json
    assert len(actual_reply) == 3

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_cinema_14_booking_records_user_success(mock_get):
    client = app.test_client()
    response = client.get("/bookings/{}".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":8.8,"title":"Creed","uri":"/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"}]}\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_MOVIES))
def test_cinema_14_booking_records_user_fail_movies(mock_get):
    client = app.test_client()
    response = client.get("/bookings/{}".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Movie service is unavailable.</p>\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MOVIES_TIMEOUT))
def test_cinema_14_booking_records_user_timeout_movies(mock_get):
    client = app.test_client()
    response = client.get("/bookings/{}".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Movie service timed out.</p>\n'

def test_cinema_14_booking_records_unknown_user():
    client = app.test_client()
    reply = client.get("/bookings/{}".format("cmeik"))
    actual_reply = reply.json
    assert actual_reply == None
    assert reply.status_code == 404

GOOD_RESPONSES = {
  "chris_rivers": {
    "20151201": [
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ]
  }
}