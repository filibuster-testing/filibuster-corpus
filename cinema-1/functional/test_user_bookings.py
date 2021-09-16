import requests

import os
import sys

from filibuster.assertions import was_fault_injected

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper 
helper = helper.Helper("cinema-1")

def test_functional_cinema_1_user_user_bookings():
    users_bookings = requests.get("{}/users/{}/bookings".format(helper.get_service_url('users'), 'chris_rivers'), timeout=helper.get_timeout('bookings'))
    if users_bookings.status_code == 200:
        assert (not was_fault_injected()) and users_bookings.json() == {'20151201': [{'rating': 8.8,'title': 'Creed','uri': '/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6'}]}
    else:
        assert was_fault_injected() and users_bookings.status_code in [503, 404]

if __name__ == "__main__":
    test_functional_cinema_1_user_user_bookings()