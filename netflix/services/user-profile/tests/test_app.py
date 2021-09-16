import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from user-profile.app import app

def test_profile_success():
  client = app.test_client()
  reply = client.get("/users/chris_rivers")
  assert reply.status_code == 200
  assert reply.json == RESPONSE

def test_profile_not_found():
  client = app.test_client()
  reply = client.get("/users/userNotExist")
  assert reply.status_code == 404


RESPONSE = {
  "id": "chris_rivers",
  "name": "Chris Rivers",
  "email": "chris_rivers@netflix.com"
}
