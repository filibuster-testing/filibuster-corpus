#!/usr/bin/env python

import requests
import os
import sys

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper
helper = helper.Helper("case-study-1-food-delivery-example-1")

# Note that tests should be prefixed with test_functional for filibuster compatibility
def test_create_update_delete():
    response = requests.get("{}/orders/create".format(helper.get_service_url('orders')), timeout=helper.get_timeout('orders'))
    #assert response.status_code == 200 and response.text == "authorized"
    print(response.text)

    response = requests.get("{}/orders/update".format(helper.get_service_url('orders')), timeout=helper.get_timeout('orders'))
    #assert response.status_code == 200 and response.text == "authorized"
    print(response.text)

    response = requests.get("{}/orders/delete".format(helper.get_service_url('orders')), timeout=helper.get_timeout('orders'))
    #assert response.status_code == 200 and response.text == "authorized"
    print(response.text)

if __name__ == "__main__":
    test_create_update_delete()