from http.client import responses
from flask import Flask, jsonify, request
from werkzeug.exceptions import ServiceUnavailable
from circuitbreaker import circuit
import requests
import os
import sys
import json

examples_path = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    )
)
sys.path.append(examples_path)

import helper

helper = helper.Helper("case-study-2-food-delivery-example-b")

app = Flask(__name__)

## Instrument using filibuster
sys.path.append(os.path.dirname(examples_path))

from filibuster.instrumentation.requests import (
    RequestsInstrumentor as FilibusterRequestsInstrumentor,
)

FilibusterRequestsInstrumentor().instrument(
    service_name="orders", filibuster_url=helper.get_service_url("filibuster")
)

from filibuster.instrumentation.flask import (
    FlaskInstrumentor as FilibusterFlaskInstrumentor,
)

FilibusterFlaskInstrumentor().instrument_app(
    app, service_name="orders", filibuster_url=helper.get_service_url("filibuster")
)

# filibuster requires a health check app to ensure service is running
@app.route("/health-check", methods=["GET"])
def orders_health_check():
    return jsonify({"status": "OK"})


order_counter = 0


@app.route("/orders/delivery", methods=["POST"])
def create_delivery_order():
    global order_counter
    data = request.json
    order_counter += 1

    return rpc_auth_create(
        "POST",
        "delivery_auth",
        {"order_id": order_counter, "order_amount": data["order_amount"]},
    )


@app.route("/orders/delivery", methods=["PUT"])
def update_delivery_order():
    data = request.json
    order_details = {"order_id": data["order_id"], "order_amount": data["order_amount"]}

    return rpc_auth_update("PUT", "delivery_auth", order_details)


@app.route("/orders/delivery", methods=["DELETE"])
def delete_delivery_order():
    data = request.json
    order_details = {"order_id": data["order_id"], "order_amount": data["order_amount"]}

    return rpc_auth_delete("DELETE", "delivery_auth", order_details)


@app.route("/orders/takeout", methods=["POST"])
def create_takeout_order():
    global order_counter
    data = request.json
    order_counter += 1

    return rpc_auth_create(
        "POST",
        "takeout_auth",
        {"order_id": order_counter, "order_amount": data["order_amount"]},
    )


@app.route("/orders/takeout", methods=["PUT"])
def update_takeout_order():
    data = request.json
    order_details = {"order_id": data["order_id"], "order_amount": data["order_amount"]}

    return rpc_auth_update("PUT", "takeout_auth", order_details)


@app.route("/orders/takeout", methods=["DELETE"])
def delete_takeout_order():
    data = request.json
    order_details = {"order_id": data["order_id"], "order_amount": data["order_amount"]}

    return rpc_auth_delete("DELETE", "takeout_auth", order_details)


@circuit
def rpc_auth_delete(verb, auth_type, order_details):
    return rpc_auth(verb, auth_type, order_details)


@circuit
def rpc_auth_update(verb, auth_type, order_details):
    return rpc_auth(verb, auth_type, order_details)


@circuit
def rpc_auth_create(verb, auth_type, order_details):
    return rpc_auth(verb, auth_type, order_details)


# This method communicates with the Auth and Takeout_Auth services to approve authorization requests for CRUD operations on orders
def rpc_auth(verb, auth_type, order_details):

    try:
        # here we are communicating with the auth service

        response = requests.request(
            verb,
            "{}/{}".format(helper.get_service_url("auth"), auth_type),
            timeout=helper.get_timeout("auth"),
            json={"order_details": order_details},
        )

    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The authorization service timed out.")
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("Unable to connect to the authorization service.")

    if response.status_code != 201 and response.status_code != 200:
        raise ServiceUnavailable("The authorization service is malfunctioning.")

    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=helper.get_port("orders"), host="0.0.0.0", debug=helper.get_debug())
