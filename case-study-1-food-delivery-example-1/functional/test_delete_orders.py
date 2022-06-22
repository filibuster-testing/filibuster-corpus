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
def test_delete_orders():
     
    response = requests.delete("{}/orders/1234".format(helper.get_service_url('orders')), timeout=helper.get_timeout('orders'), json={"order_id": 1234, "order_amount": 11.89})
    assert response.status_code == 200 
    



if __name__ == "__main__":

    test_delete_orders()


   