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

helper = helper.Helper("case-study-2-food-delivery-example-d")


def create_order(order_type):
    order_amount = 11.89
    response = requests.post(
        "{}/orders".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_amount": order_amount, "order_type": order_type},
    )
    return response


def delete_order(order_type):
    response = requests.delete(
        "{}/orders".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 10, "order_amount": 15.89, "order_type": order_type},
    )
    return response


def update_order(order_type):
    response = requests.put(
        "{}/orders".format(helper.get_service_url("orders")),
        timeout=helper.get_timeout("orders"),
        json={"order_id": 10, "order_amount": 15.89, "order_type": order_type},
    )
    return response


if __name__ == "__main__":

    # If 'DELETE_FAULT' environment variable is set, authorization is refused for deleting all takeout orders.
    # Note that 'DELETE_FAULT must be set for both the Takeout Auth service and this test file.
    if os.environ.get("DELETE_FAULT"):

        # these assertions will be true, becuase authorization is being granted for everything except deleting takout orders
        create_delivery_response = create_order("delivery")
        assert create_delivery_response.status_code == 201

        update_delivery_response = update_order("delivery")
        assert update_delivery_response.status_code == 200

        delete_delivery_response = delete_order("delivery")
        assert delete_delivery_response.status_code == 200

        create_takeout_response = create_order("takeout")
        assert create_takeout_response.status_code == 201

        update_takeout_response = update_order("takeout")
        assert update_takeout_response.status_code == 200

        # five repeated failures to authorize deleting a takeout order will trip the corresponding circuit breaker.
        # As a result of this, on the six attempt to delete a takeout order, we will see the status code change from 500 to 503,
        # since the circuit breaker is now open and rendering the Takeout Auth service unavailable.
        for i in range(6):
            delete_takeout_response = delete_order("takeout")
            try:
                assert delete_takeout_response.status_code == 200
            except AssertionError as e:
                print(
                    "Assertion error for delete authorization: status code",
                    delete_takeout_response.status_code,
                )

        # Authorization for creating and updating orders still functions properly, since those operations
        # have seperate invocation paths from deleting orders.
        create_delivery_response = create_order("delivery")
        assert create_delivery_response.status_code == 201

        update_delivery_response = update_order("delivery")
        assert update_delivery_response.status_code == 200

        create_takeout_response = create_order("takeout")
        assert create_takeout_response.status_code == 201

        update_takeout_response = update_order("takeout")
        assert update_takeout_response.status_code == 200

        # Becuase delivery and takeout orders use the same invocation path for deleting methods (via the 'rpc_auth_delete' method)
        # the open circuit breaker now prevents authorization for both kinds of orders, so this assertion will fail
        delete_delivery_response = delete_order("delivery")
        assert delete_delivery_response.status_code == 200

    # If 'DELETE_FAULT' is not set, everything functions as intended, and authorization is granted for all order operations
    else:

        # these assertions will all be true
        create_delivery_response = create_order("delivery")
        assert create_delivery_response.status_code == 201

        update_delivery_response = update_order("delivery")
        assert update_delivery_response.status_code == 200

        delete_delivery_response = delete_order("delivery")
        assert delete_delivery_response.status_code == 200

        create_takeout_response = create_order("takeout")
        assert create_takeout_response.status_code == 201

        update_takeout_response = update_order("takeout")
        assert update_takeout_response.status_code == 200

        delete_takeout_response = delete_order("takeout")
        assert delete_takeout_response.status_code == 200
