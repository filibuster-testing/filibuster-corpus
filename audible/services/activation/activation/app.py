
# Activation service (EC2)

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound

import json
import os
import sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("audible")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="activation",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="activation", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="activation", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

with open("{}/activation.json".format(parent_path), "r") as f:
    books = json.load(f)

@app.route("/books/<book_id>", methods=['GET'])
def get_license(book_id):
    response = {}
    if not book_id in books:
        raise NotFound("book_id {} not found".format(book_id))

    response["license"] = books[book_id]
    return jsonify(response)


if __name__ == "__main__":
    app.run(port=helper.get_port('activation'), host="0.0.0.0", debug=helper.get_debug())
