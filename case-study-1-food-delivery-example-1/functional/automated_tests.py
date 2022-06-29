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

helper = helper.Helper("case-study-1-food-delivery-example-1")


def test_create_orders():
    order_amount = 11.89
    response = requests.post(
        "{}/orders".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_amount": order_amount},
    )
    try:
        assert (
            response.status_code == 201
            and response.json()["order_details"]["order_amount"] == order_amount
            and response.json()["order_details"]["order_id"] is not None
        )
    except AssertionError as e:
        return(e)


def test_delete_orders():
    order_amount = 15.89
    response = requests.delete(
        "{}/orders/10".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 1234, "order_amount": order_amount},
    )
    try:
        assert (
            response.status_code == 200
            and response.json()["order_details"]["order_amount"] == order_amount
            and response.json()["order_details"]["order_id"] == 10
        )
    except AssertionError as e:
        return(e)


def test_update_orders():
    order_amount = 15.89
    response = requests.put(
        "{}/orders/10".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 1234, "order_amount": order_amount},
    )
    try:
        assert (
            response.status_code == 200
            and response.json()["order_details"]["order_amount"] == order_amount
            and response.json()["order_details"]["order_id"] == 10
        )
    except AssertionError as e:
        return(e)


if __name__ == "__main__":

    #running this loop will trip the circuit breaker if 'DELETE_FAULT' is set
    for i in range(5):
        test_delete_orders()  

    # If the circuit breaker is tripped, these assertions will fail 
    test_create_orders()
    test_update_orders()
    