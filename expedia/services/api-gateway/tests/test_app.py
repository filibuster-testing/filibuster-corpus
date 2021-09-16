import requests
import os, sys
import enum

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from api-gateway.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("expedia")

class MockFailure(enum.Enum):
  SUCCESS = 0
  REVIEW_ML_FAIL = 1
  REVIEW_ML_TIMEOUT = 2
  REVIEW_ML_NOT_FOUND = 3
  REVIEW_ML_FAIL_REVIEW_TIME_FAIL = 4
  REVIEW_ML_FAIL_REVIEW_TIME_TIMEOUT = 5
  REVIEW_ML_FAIL_REVIEW_TIME_NOT_FOUND = 6


class MockResponse:
    def __init__(self, data, status_code):
      self.data = data
      self.status_code = status_code

    def json(self):
      return self.data

def mock_requests_get_with_failure_setting(failure_setting):
  def mock_requests_get(*args, **kwargs):
    review_ml_request = "http://{}:{}/hotels/hotel1".format(
        helper.resolve_requests_host('review-ml'), helper.get_port('review-ml'))
    if args == (review_ml_request,):
      if failure_setting in [MockFailure.REVIEW_ML_FAIL, MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_FAIL, MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_TIMEOUT, MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_NOT_FOUND]:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.REVIEW_ML_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.REVIEW_ML_NOT_FOUND:
        return MockResponse({}, 404)
      else:
        return MockResponse(ML_RESPONSE, 200)

    review_time_request = "http://{}:{}/hotels/hotel1".format(
        helper.resolve_requests_host('review-time'), helper.get_port('review-time'))
    if args == (review_time_request,):
      if failure_setting == MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_FAIL:
        raise requests.exceptions.ConnectionError
      elif failure_setting == MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_TIMEOUT:
        raise requests.exceptions.Timeout
      elif failure_setting == MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_NOT_FOUND:
        return MockResponse({}, 404)
      else:
        return MockResponse(TIME_RESPONSE, 200)

  return mock_requests_get



@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_success(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 200
  response = reply.json
  assert response == ML_RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_FAIL))
def test_review_ml_fail(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 200
  response = reply.json
  assert response == TIME_RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_TIMEOUT))
def test_review_ml_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 200
  response = reply.json
  assert response == TIME_RESPONSE


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_NOT_FOUND))
def test_review_ml_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 404


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_FAIL))
def test_review_ml_fail_review_time_fail(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_TIMEOUT))
def test_review_ml_fail_review_time_timeout(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.REVIEW_ML_FAIL_REVIEW_TIME_NOT_FOUND))
def test_review_ml_fail_review_time_not_found(mock_get):
  client = app.test_client()
  reply = client.get("/review/hotels/hotel1")
  assert reply.status_code == 404


ML_RESPONSE = {
    "reviews": [
        {
            "review": "Best hotel ever!",
            "rating": 10,
            "timestamp": "2018-07-21"
        },
        {
            "review": "The rooms are quite clean.",
            "rating": 8,
            "timestamp": "2019-03-01"
        },
        {
            "review": "Very nice service.",
            "rating": 9,
            "timestamp": "2017-05-09"
        }
    ]
}

TIME_RESPONSE = {
    "reviews": [
        {
            "review": "The rooms are quite clean.",
            "rating": 8,
            "timestamp": "2019-03-01"
        },
        {
            "review": "Best hotel ever!",
            "rating": 10,
            "timestamp": "2018-07-21"
        },
        {
            "review": "Very nice service.",
            "rating": 9,
            "timestamp": "2017-05-09"
        }
    ]
}
