import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from review-time.app import app

def test_reviews_success():
  client = app.test_client()
  reply = client.get("/hotels/hotel1")
  assert reply.status_code == 200
  assert reply.json == RESPONSE

def test_ratings_not_found():
  client = app.test_client()
  reply = client.get("/hotels/hotelNotExist")
  assert reply.status_code == 404


RESPONSE = {
    "reviews": [
        {
            "review": "The rooms are quite clean.",
            "rating": 8,
            "timestamp": "2019-03-01"
        },
        {
            "review": "Best hotel ever!",
            "rating": 10,
            "timestamp": "2018-07-21"
        },
        {
            "review": "Very nice service.",
            "rating": 9,
            "timestamp": "2017-05-09"
        }
    ]
}
