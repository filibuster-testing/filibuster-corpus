import pytest
import json
import sys
import os

if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  from unittest import mock
else:
  import mock

from monolith.app import app

parent_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(parent_path)
import helper 
helper = helper.Helper("cinema-8")

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
with open("{}/cinema-8/services/monolith/users.json".format(examples_path), "r") as f:
    users = json.load(f)


def test_cinema_8_monolith_success():
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("chris_rivers"))
    assert response.get_data() == b'{"20151201":[{"rating":8.8,"title":"Creed","uri":"/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6"}]}\n'
    
def test_cinema_8_monolith_not_found():
    client = app.test_client()
    response = client.get("/users/{}/bookings".format("not_found"))
    assert response.status_code == 404
