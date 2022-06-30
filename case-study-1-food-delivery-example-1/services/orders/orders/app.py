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

helper = helper.Helper("case-study-1-food-delivery-example-1")

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


@app.route("/orders", methods=["POST"])
def create_order():
    global order_counter
    data = request.json
    order_amount = data["order_amount"]
    order_counter += 1

    return rpc_auth("POST", {"order_id": order_counter, "order_amount": order_amount})


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.json
    order_amount = data["order_amount"]
    order_details = {"order_id": order_id, "order_amount": order_amount}

    return rpc_auth("PUT", order_details)


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    data = request.json
    order_amount = data["order_amount"]
    order_details = {"order_id": order_id, "order_amount": order_amount}

    return rpc_auth("DELETE", order_details)


# This method communicates with the Auth service. It handles all authorization requests from the create, update, and delete methods
@circuit
def rpc_auth(verb, order_details):
    try:
        response = requests.request(
            verb,
            "{}/auth".format(helper.get_service_url("auth")),
            timeout=helper.get_timeout("auth"),
            json={"order_details": order_details},
        )
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The authorization service timed out.")
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("Unable to connect to the authorization service.")

    if response.status_code != 200 and response.status_code != 201:
        raise ServiceUnavailable("The authorization service is malfunctioning.")

    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=helper.get_port("orders"), host="0.0.0.0", debug=helper.get_debug())
