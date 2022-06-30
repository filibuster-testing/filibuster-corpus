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
    return response


def test_delete_orders():
    order_amount = 15.89
    response = requests.delete(
        "{}/orders/10".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 10, "order_amount": order_amount},
    )
    return response


def test_update_orders():
    order_amount = 15.89
    response = requests.put(
        "{}/orders/10".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 10, "order_amount": order_amount},
    )
    return response


if __name__ == "__main__":

    # If 'DELETE_FAULT' is set, authorization is refused for all delete orders
    # Note that 'DELETE_FAULT must be set for both the auth service and this test file
    if os.environ.get("DELETE_FAULT"):

        # these assertions will be true, becuase the auth service is still functioning for create and update
        create_response = test_create_orders()
        assert create_response.status_code == 201

        update_response = test_update_orders()
        assert update_response.status_code == 200

        # the repeated failure of the delete authorization will trip the circuit breaker
        for i in range(6):
            delete_response = test_delete_orders()
            try:
                assert delete_response.status_code == 200
            except AssertionError as e:
                print(
                    "Assertion error for delete authorization: status code",
                    delete_response.status_code,
                )

        # the open circuit breaker prevents authorization for create or update,
        # even though they were functioning properly
        response = test_create_orders()
        assert response.status_code == 201

        response = test_update_orders()
        assert response.status_code == 200

    # If 'DELETE_FAULT' is not set, authorization works for all create, update, and delete
    else:

        # these assertions will be true, becuase the auth service is functioning properly
        create_response = test_create_orders()
        assert create_response.status_code == 201

        update_response = test_update_orders()
        assert update_response.status_code == 200

        delete_response = test_delete_orders()
        assert delete_response.status_code == 200
