import requests
import os, sys
import enum

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from content-delivery-service.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("audible")

class MockFailure(enum.Enum):
  SUCCESS = 0
  ADS_FAIL = 1
  ADS_TIMEOUT = 2
  ADS_NOT_FOUND = 3
  ADS_FORBIDDEN = 4
  ADS_SERVICE_UNAVAILABLE = 5
  ADS_INTERNAL_SERVER_ERROR = 6
  METADATA_FAIL = 7
  METADATA_TIMEOUT = 8
  METADATA_NOT_FOUND = 9
  METADATA_FORBIDDEN = 10
  AUDIO_FAIL = 11
  AUDIO_TIMEOUT = 12
  AUDIO_NOT_FOUND = 13
  AUDIO_FORBIDDEN = 14

class MockResponse:
    def __init__(self, data, status_code):
      self.data = data
      self.content = data
      self.status_code = status_code

    def json(self):
      return self.data

def mock_requests_get_with_failure_setting(failure_setting):
  def mock_requests_get(*args, **kwargs):
    ads_request = "{}/users/user1/books/book2".format(helper.get_service_url("audible-download-service"))
    if args == (ads_request,):
      if failure_setting == MockFailure.ADS_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.ADS_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.ADS_NOT_FOUND:
        status_code = 404
      elif failure_setting == MockFailure.ADS_FORBIDDEN:
        status_code = 403
      elif failure_setting == MockFailure.ADS_SERVICE_UNAVAILABLE:
        status_code = 503
      elif failure_setting == MockFailure.ADS_INTERNAL_SERVER_ERROR:
        status_code = 500
      else:
        status_code = 200
      return MockResponse(ADS_RESPONSE, status_code)

    metadata_request = "{}/books/book2/licenses/".format(helper.get_service_url("asset-metadata")) + ADS_RESPONSE["license"]
    if args == (metadata_request,):
      if failure_setting == MockFailure.METADATA_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.METADATA_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.METADATA_NOT_FOUND:
        status_code = 404
      elif failure_setting == MockFailure.METADATA_FORBIDDEN:
        status_code = 403
      else:
        status_code = 200
      return MockResponse(METADATA_RESPONSE, status_code)

    audio_request = "{}/books/book2/licenses/".format(helper.get_service_url("audio-assets")) + ADS_RESPONSE["license"]
    if args == (audio_request,):
      if failure_setting == MockFailure.AUDIO_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.AUDIO_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.AUDIO_NOT_FOUND:
        status_code = 404
      elif failure_setting == MockFailure.AUDIO_FORBIDDEN:
        status_code = 403
      else:
        status_code = 200
      return MockResponse(AUDIO_RESPONSE, status_code)
  return mock_requests_get


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_cds_success(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 200
  assert reply.data == AUDIO_RESPONSE

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_FAIL))
def test_cds_ads_fail(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_TIMEOUT))
def test_cds_ads_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_NOT_FOUND))
def test_cds_ads_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_FORBIDDEN))
def test_cds_ads_forbidden(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 403

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_SERVICE_UNAVAILABLE))
def test_cds_ads_service_unavailable(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.ADS_INTERNAL_SERVER_ERROR))
def test_cds_ads_internal_server_error(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 500

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.METADATA_FAIL))
def test_cds_metadata_fail(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.METADATA_TIMEOUT))
def test_cds_metadata_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.METADATA_NOT_FOUND))
def test_cds_metadata_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.METADATA_FORBIDDEN))
def test_cds_metadata_forbidden(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 403

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.AUDIO_FAIL))
def test_cds_audio_fail(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.AUDIO_TIMEOUT))
def test_cds_audio_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 503

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.AUDIO_NOT_FOUND))
def test_cds_audio_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.AUDIO_FORBIDDEN))
def test_cds_audio_forbidden(mock_get):
  client = app.test_client()
  reply = client.get("/users/user1/books/book2")
  assert reply.status_code == 403


ADS_RESPONSE = {
    "license": "745c723e03084d27553fb9d4037b08c1"
}

METADATA_RESPONSE = {
    "title": "Harry Potter and the Philosopher's Stone",
    "author": "J. K. Rowling",
    "chapters": [
        {
            "id": 1,
            "title": "The Boy Who Lived",
            "location": "0:00:00"
        },
        {
            "id": 2,
            "title": "The Vanishing Glass",
            "location": "1:00:00"
        },
        {
            "id": 3,
            "title": "The Letters from No One",
            "location": "2:00:00"
        },
        {
            "id": 4,
            "title": "The Keeper of Keys",
            "location": "3:00:00"
        }
    ]
}

AUDIO_RESPONSE = b"This is book 2."
