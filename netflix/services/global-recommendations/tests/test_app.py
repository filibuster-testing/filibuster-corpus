import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from global-recommendations.app import app

def test_my_list_success():
    client = app.test_client()
    reply = client.get("/")
    assert reply.status_code == 200
    assert reply.json == RESPONSE


RESPONSE = {
    "recommendations": ["Inception", "Shutter Island", "The Dark Night"]
}
