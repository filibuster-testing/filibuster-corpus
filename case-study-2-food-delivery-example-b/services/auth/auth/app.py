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

helper = helper.Helper("case-study-2-food-delivery-example-b")

app = Flask(__name__)

## Instrument using filibuster

sys.path.append(os.path.dirname(examples_path))

from filibuster.instrumentation.requests import (
    RequestsInstrumentor as FilibusterRequestsInstrumentor,
)

FilibusterRequestsInstrumentor().instrument(
    service_name="auth", filibuster_url=helper.get_service_url("filibuster")
)

from filibuster.instrumentation.flask import (
    FlaskInstrumentor as FilibusterFlaskInstrumentor,
)

FilibusterFlaskInstrumentor().instrument_app(
    app, service_name="auth", filibuster_url=helper.get_service_url("filibuster")
)

# filibuster requires a health check app to ensure service is running
@app.route("/health-check", methods=["GET"])
def auth_health_check():
    return jsonify({"status": "OK"})


# This method grants authorization to delete a delivery order
@app.route("/delivery_auth", methods=["DELETE"])
def auth_delete_delivery():
    return jsonify(request.json), 200


# This method grants authorization to update a delivery order
@app.route("/delivery_auth", methods=["PUT"])
def auth_put_delivery():
    return jsonify(request.json), 200


# This method grants authorization to create a delivery order
@app.route("/delivery_auth", methods=["POST"])
def auth_post_delivery():
    return jsonify(request.json), 201


# This method grants authorization to delete a takeout order
# If the 'DELETE_FAULTS' enivornment variable is set at runtime, it will
# refuse authorization for deleting takeout orders.
@app.route("/takeout_auth", methods=["DELETE"])
def auth_delete_takeout():
    if os.environ.get("DELETE_FAULT", ""):
        return jsonify(request.json), 500
    else:
        return jsonify(request.json), 200


# This method grants authorization to update a takeout order
@app.route("/takeout_auth", methods=["PUT"])
def auth_put_takeout():
    return jsonify(request.json), 200


# This method grants authorization to create a takeout order
@app.route("/takeout_auth", methods=["POST"])
def auth_post_takeout():
    return jsonify(request.json), 201


if __name__ == "__main__":
    app.run(port=helper.get_port("auth"), host="0.0.0.0", debug=helper.get_debug())
