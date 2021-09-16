import os, sys

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from db-primary.app import app

def test_read_success():
    client = app.test_client()
    reply = client.get("/read")
    assert reply.status_code == 200


def test_write_success():
    client = app.test_client()
    reply = client.post("/write/urls/url")
    assert reply.status_code == 200


#TODO: test_write_fail()
