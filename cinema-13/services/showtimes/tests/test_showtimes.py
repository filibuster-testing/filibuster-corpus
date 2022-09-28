import requests
import sys
import os

from showtimes.app import app

def test_cinema_13_showtimes_index():
    client = app.test_client()
    reply = client.get("/")
    actual_reply = reply.json
    assert reply.status_code == 200

def test_cinema_13_booking_showtimes_showtimes():
    client = app.test_client()
    reply = client.get("/showtimes")
    actual_reply = reply.json
    assert len(actual_reply) == 6

def test_cinema_13_booking_showtimes_showtime():
    client = app.test_client()
    for date, expected in GOOD_RESPONSES.items():
        reply = client.get("/showtimes/{}".format(date))
        actual_reply = reply.json
        assert len(actual_reply) == len(expected)
        assert set(actual_reply) == set(expected)

def test_cinema_13_booking_showtimes_invalid_showtime():
    client = app.test_client()
    reply = client.get("/showtimes/{}".format("1"))
    actual_reply = reply.json
    assert actual_reply == None
    assert reply.status_code == 404

GOOD_RESPONSES = {
    "20151130": [
        "720d006c-3a57-4b6a-b18f-9b713b073f3c",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
    ],
    "20151201": [
        "267eedb8-0f5d-42d5-8f43-72426b9fb3e6",
        "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae"
    ],
    "20151202": [
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "96798c08-d19b-4986-a05d-7da856efb697",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab",
        "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
    ],
    "20151203": [
        "720d006c-3a57-4b6a-b18f-9b713b073f3c",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
    ],
    "20151204": [
        "96798c08-d19b-4986-a05d-7da856efb697",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "7daf7208-be4d-4944-a3ae-c1c2f516f3e6"
    ],
    "20151205": [
        "96798c08-d19b-4986-a05d-7da856efb697",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
        "276c79ec-a26a-40a6-b3d3-fb242a5947b6",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
    ]
}

# if __name__ == "__main__":
#     unittest.main()