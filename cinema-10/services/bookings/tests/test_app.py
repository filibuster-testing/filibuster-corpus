import requests
import threading
import sys
import os

from bookings.app import app

def test_cinema_10_booking_records_index():
    client = app.test_client()
    reply = client.get("/")
    actual_reply = reply.json
    assert reply.status_code == 200

def test_cinema_10_booking_records_users():
    client = app.test_client()
    reply = client.get("/bookings")
    actual_reply = reply.json
    assert len(actual_reply) == 3

def test_cinema_10_booking_records_user():
    client = app.test_client()
    for username, expected in GOOD_RESPONSES.items():
        reply = client.get("/bookings/{}".format(username))
        actual_reply = reply.json
        assert len(actual_reply) == len(expected)
        assert set(actual_reply) == set(expected) 

def test_cinema_10_booking_records_unknown_user():
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
  },
  "garret_heaton": {
    "20151201": [
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ],
    "20151202": [
      "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
    ]
  },
  "dwight_schrute": {
    "20151201": [
      "7daf7208-be4d-4944-a3ae-c1c2f516f3e6",
      "267eedb8-0f5d-42d5-8f43-72426b9fb3e6"
    ],
    "20151205": [
      "a8034f44-aee4-44cf-b32c-74cf452aaaae",
      "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
    ]
  }
}