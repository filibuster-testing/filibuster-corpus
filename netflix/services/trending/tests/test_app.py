import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from trending.app import app

def test_trending_success():
    client = app.test_client()
    reply = client.get("/")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


RESPONSE = {
    "trending": ["The Croods", "Red Dot", "We Can Be Heroes"]
}
