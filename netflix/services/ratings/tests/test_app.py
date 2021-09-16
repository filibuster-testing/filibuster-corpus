import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ratings.app import app

def test_ratings_success():
    client = app.test_client()
    reply = client.get("/users/chris_rivers")
    assert reply.status_code == 200
    assert reply.json == RESPONSE

def test_ratings_not_found():
    client = app.test_client()
    reply = client.get("/users/userNotExist")
    assert reply.status_code == 404


RESPONSE = {
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
