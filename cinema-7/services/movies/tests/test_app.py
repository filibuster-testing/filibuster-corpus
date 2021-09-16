import requests
import sys
import os

from movies.app import app

def test_cinema_7_movies_movie_not_found():
    client = app.test_client()
    reply = client.get("movies/{}".format("1"))
    actual_reply = reply.json
    assert actual_reply == None
    assert reply.status_code == 404

def test_cinema_7_movies_movie():
    client = app.test_client()
    for movieid, expected in GOOD_RESPONSES.items():
        reply = client.get("movies/{}".format(movieid))
        expected['uri'] = "/movies/{}".format(movieid)
        actual_reply = reply.json
        assert set(actual_reply.items()) == set(expected.items())

def test_cinema_7_movies_movies():
    client = app.test_client()
    reply = client.get("/movies")
    actual_reply = reply.json
    assert len(actual_reply) == 7

def test_cinema_7_movies_index():
    client = app.test_client()
    reply = client.get("/")
    actual_reply = reply.json
    assert reply.status_code == 200

GOOD_RESPONSES = {
  "720d006c-3a57-4b6a-b18f-9b713b073f3c": {
    "title": "The Good Dinosaur",
    "rating": 7.4,
    "director": "Peter Sohn",
    "id": "720d006c-3a57-4b6a-b18f-9b713b073f3c"
  },
  "a8034f44-aee4-44cf-b32c-74cf452aaaae": {
    "title": "The Martian",
    "rating": 8.2,
    "director": "Ridley Scott",
    "id": "a8034f44-aee4-44cf-b32c-74cf452aaaae"
  },
  "96798c08-d19b-4986-a05d-7da856efb697": {
    "title": "The Night Before",
    "rating": 7.4,
    "director": "Jonathan Levine",
    "id": "96798c08-d19b-4986-a05d-7da856efb697"
  },
  "267eedb8-0f5d-42d5-8f43-72426b9fb3e6": {
    "director": "Ryan Coogler",
    "id": "267eedb8-0f5d-42d5-8f43-72426b9fb3e6",
    "rating": 8.8,
    "title": "Creed"
  },
  "7daf7208-be4d-4944-a3ae-c1c2f516f3e6": {
    "title": "Victor Frankenstein",
    "rating": 6.4,
    "director": "Paul McGuigan",
    "id": "7daf7208-be4d-4944-a3ae-c1c2f516f3e6"
  },
  "276c79ec-a26a-40a6-b3d3-fb242a5947b6": {
    "title": "The Danish Girl",
    "rating": 5.3,
    "director": "Tom Hooper",
    "id": "276c79ec-a26a-40a6-b3d3-fb242a5947b6"
  },
  "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab": {
    "title": "Spectre",
    "rating": 7.1,
    "director": "Sam Mendes",
    "id": "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
  }
}