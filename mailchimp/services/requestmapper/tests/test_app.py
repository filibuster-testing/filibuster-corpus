import os, sys

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

from requestmapper.app import app


def test_success():
    client = app.test_client()
    reply = client.get("/urls/prettyurl")
    assert reply.status_code == 200
    assert reply.json["result"] == "internalurl"

