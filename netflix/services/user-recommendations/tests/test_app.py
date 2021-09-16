import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from user-recommendations.app import app

def test_user_recommendations_success():
  client = app.test_client()
  reply = client.get("/users/chris_rivers")
  assert reply.status_code == 200
  assert reply.json == RESPONSE

def test_user_recommendations_not_found():
  client = app.test_client()
  reply = client.get("/users/userNotExist")
  assert reply.status_code == 404


RESPONSE = {
    "recommendations": ["Harry Potter and the Order of the Phoenix", "Harry Potter and the Half-Blood Prince", "Harry Potter and the Deathly Hallows"],
}
