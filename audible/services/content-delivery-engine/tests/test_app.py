import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from content-delivery-engine.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("audible")

def test_cde_success():
  client = app.test_client()
  reply = client.get("/users/user1/books/book1")
  assert reply.status_code == 200
  assert (reply.json["url"] == "{}/users/user1/books/book1".format(helper.get_service_url("content-delivery-service")))

def test_cde_invalid_book():
  client = app.test_client()
  reply = client.get("/users/user1/books/bookNotExist")
  assert reply.status_code == 404
