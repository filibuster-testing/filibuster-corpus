#!/usr/bin/env python

import requests
import os
import sys
import json

examples_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
sys.path.append(examples_path)

import helper

helper = helper.Helper("case-study-1-food-delivery-example-2")

# Note that tests should be prefixed with test_functional for filibuster compatibility
def test_delete_orders():
    order_amount = 15.89
    response = requests.delete(
        "{}/orders/10".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 1234, "order_amount": order_amount},
    )
    assert (
        response.status_code == 200
        and response.json()["order_details"]["order_amount"] == order_amount
        and response.json()["order_details"]["order_id"] == 10
    )


if __name__ == "__main__":
    test_delete_orders()
