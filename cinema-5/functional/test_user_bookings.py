import requests

import os
import sys

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper 
helper = helper.Helper("cinema-5")

# A user should be able to check the movies they have booked.
def test_functional_cinema_5_user_user_bookings():
    users_bookings = requests.get("{}/users/{}/bookings".format(helper.get_service_url('users'), 'chris_rivers'), timeout=helper.get_timeout('bookings'))
    if users_bookings.status_code == 200:
        assert users_bookings.json() == {'20151201': [{'rating': 8.8,'title': 'Creed','uri': '/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6'}]}
    else:
        assert helper.fault_injected() and users_bookings.status_code in [503, 404]

if __name__ == "__main__":
    test_functional_cinema_5_user_user_bookings()