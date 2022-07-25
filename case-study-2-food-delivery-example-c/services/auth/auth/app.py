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

helper = helper.Helper("case-study-2-food-delivery-example-c")

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


# This method grants authorization to delete takeout and delivers orders
# If the 'DELETE_FAULTS' enivornment variable is set at runtime, it will
# refuse authorization for deleting takeout orders.
@app.route("/auth", methods=["DELETE"])
def auth_delete_takeout():
    data = request.json
    if str(data["order_type"]) == "delivery":
        return jsonify(request.json), 200
    elif data["order_type"] == "takeout":
        if os.environ.get("DELETE_FAULT", ""):
            return jsonify(request.json), 500
        else:
            return jsonify(request.json), 200
    else:
        return jsonify(request.json), 403


# This method grants authorization to update a takeout/delivery order
@app.route("/auth", methods=["PUT"])
def auth_put_takeout():
    data = request.json
    if str(data["order_type"]) == "delivery" or str(data["order_type"]) == "takeout":
        return jsonify(request.json), 200
    else:
        return jsonify(request.json), 403


# This method grants authorization to create a takeout/delivery order
@app.route("/auth", methods=["POST"])
def auth_post_takeout():
    data = request.json
    if str(data["order_type"]) == "delivery" or str(data["order_type"]) == "takeout":
        return jsonify(request.json), 201
    else:
        return jsonify(request.json), 403


if __name__ == "__main__":
    app.run(port=helper.get_port("auth"), host="0.0.0.0", debug=helper.get_debug())
