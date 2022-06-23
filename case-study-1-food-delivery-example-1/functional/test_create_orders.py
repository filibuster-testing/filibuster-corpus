#!/usr/bin/env python

import requests
import os
import sys
import json

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(examples_path)

import helper
helper = helper.Helper("case-study-1-food-delivery-example-1")

# Note that tests should be prefixed with test_functional for filibuster compatibility
def test_create_orders():     
    order_amount = 11.89
    response = requests.post("{}/orders".format(helper.get_service_url('orders')), timeout=helper.get_timeout('orders'), json={"order_amount": order_amount})
    #data = response.json()          
    assert response.status_code == 201 and response.json()['order_details']['order_amount'] == order_amount    

if __name__ == "__main__":
    test_create_orders()