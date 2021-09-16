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

from users.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("cinema-6")

with open("{}/cinema-6/services/bookings-primary/bookings.json".format(os.path.dirname(parent_path)), "r") as f:
    bookings-primary = json.load(f)

with open("{}/cinema-6/services/bookings-secondary/bookings.json".format(os.path.dirname(parent_path)), "r") as f:
    bookings-secondary = json.load(f)

with open("{}/cinema-6/services/movies/movies.json".format(os.path.dirname(parent_path)), "r") as f:
    movies = json.load(f)

class MockFailure(enum.Enum): 
  SUCCESS = 0
  FAIL_BOOKINGS = 1
  NO_BOOKINGS_FOUND = 2
  BOOKINGS_TIMEOUT = 3
  FAIL_BOOKINGS_AND_FAIL_BOOKINGS2 = 4
  FAIL_BOOKINGS_AND_BOOKINGS2_TIMEOUT = 5
  FAIL_BOOKINGS_AND_BOOKINGS2_NOT_FOUND = 6
  FAIL_MOVIES = 7
  MOVIES_TIMEOUT = 8

def mock_requests_get_with_failure_setting(failure_setting):
  class MockResponse:
    def __init__(self, json_data, status_code):
      self.json_data = json_data
      self.status_code = status_code

    def json(self):
      return self.json_data

  success_status_code = 200
  def mock_requests_get(*args, **kwargs):
    bookings_request = "http://{}:{}/bookings/chris_rivers".format(helper.resolve_requests_host('bookings-primary'), helper.get_port('bookings-primary'))
    if (args == (bookings_request,)):
      if (failure_setting in [MockFailure.FAIL_BOOKINGS, MockFailure.FAIL_BOOKINGS_AND_FAIL_BOOKINGS2, MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_TIMEOUT, MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_NOT_FOUND]):
        raise requests.exceptions.ConnectionError
      if (failure_setting == MockFailure.BOOKINGS_TIMEOUT):
        raise requests.exceptions.Timeout
      status_code = 404 if failure_setting == MockFailure.NO_BOOKINGS_FOUND else success_status_code
      return MockResponse(bookings-primary["chris_rivers"], status_code)

    bookings2_request = "http://{}:{}/bookings/chris_rivers".format(helper.resolve_requests_host('bookings-secondary'), helper.get_port('bookings-secondary'))
    if (args == (bookings2_request,)):
      if (failure_setting == MockFailure.FAIL_BOOKINGS_AND_FAIL_BOOKINGS2):
        raise requests.exceptions.ConnectionError
      if (failure_setting == MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_TIMEOUT):
        raise requests.exceptions.Timeout
      status_code = 404 if failure_setting == MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_NOT_FOUND else success_status_code
      return MockResponse(bookings-secondary["chris_rivers"], status_code)

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

    movies2_request = "http://{}:{}/movies/7daf7208-be4d-4944-a3ae-c1c2f516f3e6".format(helper.resolve_requests_host('movies'), helper.get_port('movies'))
    if (args == (movies2_request,)):
      if (failure_setting == MockFailure.FAIL_MOVIES):
        raise requests.exceptions.ConnectionError
      if (failure_setting == MockFailure.MOVIES_TIMEOUT):
        raise requests.exceptions.Timeout
      movieid = '7daf7208-be4d-4944-a3ae-c1c2f516f3e6'
      result = movies[movieid]
      result["uri"] = "/movies/{}".format(movieid)
      return MockResponse(result, success_status_code)
    
  return mock_requests_get


def test_cinema_6_user_index():
    client = app.test_client()
    reply = client.get("/")
    assert reply.status_code == 200

def test_cinema_6_user_users():
    client = app.test_client()
    reply = client.get("/users")
    actual_reply = reply.json
    assert len(actual_reply) == 7

def test_cinema_6_user_user():
    client = app.test_client()
    for username, expected in GOOD_RESPONSES.items():
        reply = client.get("/users/{}".format(username))
        actual_reply = reply.json
        assert actual_reply == expected

def test_cinema_6_user_invalid_user():
    client = app.test_client()
    reply = client.get("/users/{}".format("1"))
    actual_reply = reply.json
    assert actual_reply == None
    assert reply.status_code == 404

def test_cinema_6_user_user_suggested():
    client = app.test_client()
    reply = client.get("/users/{}/suggested".format("chris_rivers"))
    actual_reply = reply.json
    assert actual_reply == None

def test_cinema_6_user_user_invalid_bookings():
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("cmeik"))
    assert response.get_data() in [
      # cmeik is not a valid user.
      b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>User \'cmeik\' not found.</p>\n'
    ]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_cinema_6_user_user_bookings_success(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":8.8,"title":"Creed","uri":"/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"}]}\n'
    
@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_BOOKINGS))
def test_cinema_6_user_user_bookings_fail_bookings(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":6.4,"title":"Victor Frankenstein","uri":"/movies/7daf7208-be4d-4944-a3ae-c1c2f516f3e6"}]}\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKINGS_TIMEOUT))
def test_cinema_6_user_user_bookings_timeout_bookings(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":6.4,"title":"Victor Frankenstein","uri":"/movies/7daf7208-be4d-4944-a3ae-c1c2f516f3e6"}]}\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.NO_BOOKINGS_FOUND))
def test_cinema_6_user_user_bookings_no_bookings(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":6.4,"title":"Victor Frankenstein","uri":"/movies/7daf7208-be4d-4944-a3ae-c1c2f516f3e6"}]}\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_BOOKINGS_AND_FAIL_BOOKINGS2))
def test_cinema_6_user_user_bookings_fail_bookings_and_fail_bookings2(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Bookings service is unavailable.</p>\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_TIMEOUT))
def test_cinema_6_user_user_bookings_fail_bookings_and_bookings2_timeout(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Bookings service timed out.</p>\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_BOOKINGS_AND_BOOKINGS2_NOT_FOUND))
def test_cinema_6_user_user_bookings_fail_bookings_and_bookings2_not_found(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>No bookings were found for chris_rivers</p>\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.FAIL_MOVIES))
def test_cinema_6_user_user_bookings_fail_bookings_movies(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Movie service is unavailable.</p>\n'

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MOVIES_TIMEOUT))
def test_cinema_6_user_user_bookings_timeout_movies(mock_get):
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>503 Service Unavailable</title>\n<h1>Service Unavailable</h1>\n<p>The Movie service timed out.</p>\n'

GOOD_RESPONSES = {
  "chris_rivers" : {
    "id": "chris_rivers",
    "name": "Chris Rivers",
    "last_active":1360031010
  },
  "peter_curley" : {
    "id": "peter_curley",
    "name": "Peter Curley",
    "last_active": 1360031222
  },
  "garret_heaton" : {
    "id": "garret_heaton",
    "name": "Garret Heaton",
    "last_active": 1360031425
  },
  "michael_scott" : {
    "id": "michael_scott",
    "name": "Michael Scott",
    "last_active": 1360031625
  },
  "jim_halpert" : {
    "id": "jim_halpert",
    "name": "Jim Halpert",
    "last_active": 1360031325
  },
  "pam_beesly" : {
    "id": "pam_beesly",
    "name": "Pam Beesly",
    "last_active": 1360031225
  },
  "dwight_schrute" : {
    "id": "dwight_schrute",
    "name": "Dwight Schrute",
    "last_active": 1360031202
  }
}
