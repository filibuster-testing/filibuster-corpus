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
helper = helper.Helper("netflix")

class MockFailure(enum.Enum):
    SUCCESS = 0
    USER_PROFILE_FAIL = 3
    USER_PROFILE_TIMEOUT = 4
    USER_PROFILE_NOT_FOUND = 5
    BOOKMARKS_FAIL = 6
    BOOKMARKS_TIMEOUT = 7
    BOOKMARKS_NOT_FOUND = 8
    BOOKMARKS_FAIL_TRENDING_FAIL = 9
    BOOKMARKS_FAIL_TRENDING_TIMEOUT = 10
    BOOKMARKS_FAIL_TELEMETRY_FAIL = 11
    BOOKMARKS_FAIL_TELEMETRY_TIMEOUT = 12
    MY_LIST_FAIL = 13
    MY_LIST_TIMEOUT = 14
    MY_LIST_NOT_FOUND = 15
    USER_REC_FAIL = 16
    USER_REC_TIMEOUT = 17
    USER_REC_NOT_FOUND = 18
    USER_REC_FAIL_GLOBAL_REC_FAIL = 19
    USER_REC_FAIL_GLOBAL_REC_TIMEOUT = 20
    USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_FAIL = 21
    USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_TIMEOUT = 22
    RATINGS_FAIL = 23
    RATINGS_TIMEOUT = 24
    RATINGS_NOT_FOUND = 25


class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

def mock_requests_get_with_failure_setting(failure_setting):
    def mock_requests_get(*args, **kwargs):

        user_profile_request = "{}/users/chris_rivers".format(helper.get_service_url("user-profile"))
        if args == (user_profile_request,):
            if failure_setting == MockFailure.USER_PROFILE_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.USER_PROFILE_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.USER_PROFILE_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(USER_PROFILE_RESPONSE, status_code)

        bookmarks_request = "{}/users/chris_rivers".format(helper.get_service_url("bookmarks"))
        if args == (bookmarks_request,):
            if failure_setting in [MockFailure.BOOKMARKS_FAIL, MockFailure.BOOKMARKS_FAIL_TRENDING_FAIL, MockFailure.BOOKMARKS_FAIL_TRENDING_TIMEOUT, MockFailure.BOOKMARKS_FAIL_TELEMETRY_FAIL, MockFailure.BOOKMARKS_FAIL_TELEMETRY_TIMEOUT]:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.BOOKMARKS_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.BOOKMARKS_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(BOOKMARKS_RESPONSE, status_code)

        trending_request = helper.get_service_url("trending")
        if args == (trending_request,):
            if failure_setting in [MockFailure.BOOKMARKS_FAIL_TRENDING_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_FAIL]:
                raise requests.exceptions.ConnectionError
            elif failure_setting in [MockFailure.BOOKMARKS_FAIL_TRENDING_TIMEOUT, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_TIMEOUT]:
                raise requests.exceptions.Timeout
            else:
                status_code = 200
            return MockResponse(TRENDING_RESPONSE, status_code)
        
        my_list_request = "{}/users/chris_rivers".format(helper.get_service_url("my-list"))
        if args == (my_list_request,):
            if failure_setting == MockFailure.MY_LIST_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.MY_LIST_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.MY_LIST_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(MY_LIST_RESPONSE, status_code)

        user_rec_request = "{}/users/chris_rivers".format(helper.get_service_url("user-recommendations"))
        if args == (user_rec_request,):
            if failure_setting in [MockFailure.USER_REC_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_TIMEOUT, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_TIMEOUT]:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.USER_REC_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.USER_REC_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(USER_REC_RESPONSE, status_code)

        global_rec_request = helper.get_service_url("global-recommendations")
        if args == (global_rec_request,):
            if failure_setting in [MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_FAIL, MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_TIMEOUT]:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.USER_REC_FAIL_GLOBAL_REC_TIMEOUT:
                raise requests.exceptions.Timeout
            else:
                status_code = 200
            return MockResponse(GLOBAL_REC_RESPONSE, status_code)

        ratings_request = "{}/users/chris_rivers".format(helper.get_service_url("ratings"))
        if args == (ratings_request,):
            if failure_setting == MockFailure.RATINGS_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.RATINGS_TIMEOUT:
                raise requests.exceptions.Timeout
            elif failure_setting == MockFailure.RATINGS_NOT_FOUND:
                status_code = 404
            else:
                status_code = 200
            return MockResponse(RATINGS_RESPONSE, status_code)

    return mock_requests_get


def mock_requests_post_with_failure_setting(failure_setting):
    def mock_requests_post(*args, **kwargs):
        telemetry_request = helper.get_service_url("telemetry")
        if args == (telemetry_request,):
            if failure_setting == MockFailure.BOOKMARKS_FAIL_TELEMETRY_FAIL:
                raise requests.exceptions.ConnectionError
            elif failure_setting == MockFailure.BOOKMARKS_FAIL_TELEMETRY_TIMEOUT:
                raise requests.exceptions.Timeout
            else:
                status_code = 200
            return MockResponse({}, status_code)
    return mock_requests_post



@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.SUCCESS))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_success(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_PROFILE_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_profile_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_PROFILE_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_profile_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_PROFILE_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_profile_not_found(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 404

@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_bookmarks_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_bookmarks_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_bookmarks_not_found(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TRENDING_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_bookmarks_fail_trending_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TRENDING_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_bookmarks_fail_trending_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TELEMETRY_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TELEMETRY_FAIL))
def test_api_gateway_bookmarks_fail_telemetry_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TELEMETRY_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.BOOKMARKS_FAIL_TELEMETRY_TIMEOUT))
def test_api_gateway_bookmarks_fail_telemetry_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == USER_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MY_LIST_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_my_list_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MY_LIST_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_my_list_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.MY_LIST_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_my_list_not_found(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 404


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == GLOBAL_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == GLOBAL_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_not_found(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["recommendations"] == GLOBAL_REC_RESPONSE["recommendations"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_fail_global_rec_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_FAIL_GLOBAL_REC_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_fail_global_rec_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 200
    response = reply.json
    assert len(response) == 5
    assert response["user-profile"] == USER_PROFILE_RESPONSE
    assert response["bookmarks"] == BOOKMARKS_RESPONSE["bookmarks"]
    assert response["my-list"] == MY_LIST_RESPONSE["my-list"]
    assert response["trending"] == TRENDING_RESPONSE["trending"]
    assert response["ratings"] == RATINGS_RESPONSE["ratings"]


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_fail_global_rec_fail_trending_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.USER_REC_FAIL_GLOBAL_REC_FAIL_TRENDING_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_user_rec_fail_global_rec_fail_trending_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.RATINGS_FAIL))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_ratings_fail(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.RATINGS_TIMEOUT))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_ratings_timeout(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 503


@mock.patch('requests.get', side_effect=mock_requests_get_with_failure_setting(MockFailure.RATINGS_NOT_FOUND))
@mock.patch('requests.post', side_effect=mock_requests_post_with_failure_setting(MockFailure.SUCCESS))
def test_api_gateway_ratings_not_found(mock_get, mock_post):
    client = app.test_client()
    reply = client.get("/homepage/users/chris_rivers")
    assert reply.status_code == 404



USER_PROFILE_RESPONSE = {
        "id": "chris_rivers",
        "name": "Chris Rivers",
        "email": "chris_rivers@netflix.com"
}

BOOKMARKS_RESPONSE = {
        "bookmarks": [
                {
                        "movie": "Harry Potter and the Philosopher's Stone",
                        "timecode": "01:20:00"
                },
                {
                        "movie": "Harry Potter and the Chamber of Secrets",
                        "timecode": "00:01:20"
                }
        ]
}

MY_LIST_RESPONSE = {
        "my-list": ["Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire"]
}

USER_REC_RESPONSE = {
        "recommendations": ["Harry Potter and the Order of the Phoenix", "Harry Potter and the Half-Blood Prince", "Harry Potter and the Deathly Hallows"],
}

GLOBAL_REC_RESPONSE = {
        "recommendations": ["Inception", "Shutter Island", "The Dark Night"]
}

RATINGS_RESPONSE = {
        "ratings": [
                {
                        "movie": "Harry Potter and the Philosopher's Stone",
                        "rating": 5
                },
                {
                        "movie": "Twilight",
                        "rating": 4
                }
        ]
}

TRENDING_RESPONSE = {
        "trending": ["The Croods", "Red Dot", "We Can Be Heroes"]
}
