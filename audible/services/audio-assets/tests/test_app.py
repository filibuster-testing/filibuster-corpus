import sys
import os

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from audio-assets.app import app

def test_audio_success():
  client = app.test_client()
  reply = client.get("/books/book2/licenses/some_license")
  assert reply.status_code == 200
  assert reply.data == b'This is book 2.'

def test_audio_invalid_license():
  client = app.test_client()
  reply = client.get("/books/book2/licenses/invalid_license")
  assert reply.status_code == 403

def test_audio_invalid_book():
  client = app.test_client()
  reply = client.get("/books/bookNotExist/licenses/some_icense")
  assert reply.status_code == 404
