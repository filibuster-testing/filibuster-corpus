import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ownership.app import app

def test_ownership_success():
  client = app.test_client()
  reply = client.get("/users/user1/books/book1")
  assert reply.status_code == 200

def test_ownership_invalid_user():
  client = app.test_client()
  reply = client.get("/users/userNotExist/books/book1")
  assert reply.status_code == 404

def test_ownership_unauthorized():
  client = app.test_client()
  reply = client.get("/users/user1/books/book3")
  assert reply.status_code == 403
