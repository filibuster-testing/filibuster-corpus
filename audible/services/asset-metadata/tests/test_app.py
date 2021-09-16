import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from asset-metadata.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("audible")

def test_metadata_success():
  client = app.test_client()
  reply = client.get("/books/book1/licenses/some_license")
  assert reply.status_code == 200
  metadata = reply.json
  assert metadata["metadata"] == GOOD_RESPONSE

def test_metadata_invalid_license():
  client = app.test_client()
  reply = client.get("/books/book1/licenses/invalid_license")
  assert reply.status_code == 403

def test_metadata_invalid_book():
  client = app.test_client()
  reply = client.get("/books/bookNotExist/licenses/some_icense")
  assert reply.status_code == 404

GOOD_RESPONSE = {
  "title": "Harry Potter and the Philosopher's Stone",
  "author": "J. K. Rowling",
  "chapters": [
      {
          "id": 1,
          "title": "The Boy Who Lived",
          "location": "0:00:00"
      },
      {
          "id": 2,
          "title": "The Vanishing Glass",
          "location": "1:00:00"
      },
      {
          "id": 3,
          "title": "The Letters from No One",
          "location": "2:00:00"
      },
      {
          "id": 4,
          "title": "The Keeper of Keys",
          "location": "3:00:00"
      }
  ]
}
