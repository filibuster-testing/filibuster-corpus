import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from bookmarks.app import app

def test_bookmarks_success():
    client = app.test_client()
    reply = client.get("/users/chris_rivers")
    assert reply.status_code == 200
    assert reply.json == RESPONSE

def test_bookmarks_not_found():
    client = app.test_client()
    reply = client.get("/users/userNotExist")
    assert reply.status_code == 404


RESPONSE = {
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
