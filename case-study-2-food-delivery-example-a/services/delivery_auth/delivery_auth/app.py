from flask import Flask, jsonify, request, json
from werkzeug.exceptions import ServiceUnavailable
import os
import sys

examples_path = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    )
)
sys.path.append(examples_path)

import helper

helper = helper.Helper("case-study-2-food-delivery-example-a")

app = Flask(__name__)

## Instrument using filibuster

sys.path.append(os.path.dirname(examples_path))

from filibuster.instrumentation.requests import (
    RequestsInstrumentor as FilibusterRequestsInstrumentor,
)

FilibusterRequestsInstrumentor().instrument(
    service_name="delivery_auth", filibuster_url=helper.get_service_url("filibuster")
)

from filibuster.instrumentation.flask import (
    FlaskInstrumentor as FilibusterFlaskInstrumentor,
)

FilibusterFlaskInstrumentor().instrument_app(
    app,
    service_name="delivery_auth",
    filibuster_url=helper.get_service_url("filibuster"),
)

# filibuster requires a health check app to ensure service is running
@app.route("/health-check", methods=["GET"])
def auth_health_check():
    return jsonify({"status": "OK"})


# This method grants authorization to delete an order
@app.route("/delivery_auth", methods=["DELETE"])
def auth_delete():
    return jsonify(request.json), 200


# This method grants authorization to update an order
@app.route("/delivery_auth", methods=["PUT"])
def auth_put():
    return jsonify(request.json), 200


# This method grants authorization to create an order
@app.route("/delivery_auth", methods=["POST"])
def auth_post():
    return jsonify(request.json), 201


if __name__ == "__main__":
    app.run(
        port=helper.get_port("delivery_auth"), host="0.0.0.0", debug=helper.get_debug()
    )
