import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from my-list.app import app

def test_my_list_success():
    client = app.test_client()
    reply = client.get("/users/chris_rivers")
    assert reply.status_code == 200
    assert reply.json == RESPONSE

def test_my_list_not_found():
    client = app.test_client()
    reply = client.get("/users/userNotExist")
    assert reply.status_code == 404


RESPONSE = {
    "my-list": ["Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire"]
}
