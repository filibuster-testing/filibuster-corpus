from flask import Flask, jsonify
from werkzeug.exceptions import NotFound

import json
import os
import sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("cinema-9")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="bookings",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="bookings", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="bookings", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration

with open("{}/cinema-9/services/bookings/bookings.json".format(examples_path), "r") as f:
    bookings = json.load(f)

@app.route("/", methods=['GET'])
def hello():
    return jsonify({
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<username>"
        }
    })

@app.route("/health-check", methods=['GET'])
def bookings_health_check():
    return jsonify({ "status": "OK" })

@app.route("/bookings", methods=['GET'])
def booking_list():
    return jsonify(bookings)

@app.route("/bookings/<username>", methods=['GET'])
def booking_record(username):
    if username not in bookings:
        raise NotFound
    return jsonify(bookings[username])

if __name__ == "__main__":
     app.run(port=helper.get_port('bookings'), host="0.0.0.0", debug=helper.get_debug(), threaded=True)
