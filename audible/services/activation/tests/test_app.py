import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from activation.app import app

def test_activation_success():
  client = app.test_client()
  reply = client.get("/books/book1")
  assert reply.status_code == 200

def test_activation_invalid_book():
  client = app.test_client()
  reply = client.get("books/book4")
  assert reply.status_code == 404