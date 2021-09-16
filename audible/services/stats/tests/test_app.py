import os, sys
import json

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from stats.app import app


file_path = "{}/stats.json".format(parent_path)

def test_stats_success():
  client = app.test_client()
  reply = client.post("/users/user1/books/book1")
  assert reply.status_code == 201

  with open(file_path, "r") as f:
    stats = json.load(f)
    log = stats["logs"][-1]
    assert log['user_id'] == "user1" and log['book_id'] == "book1"
