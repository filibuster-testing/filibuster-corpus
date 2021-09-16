
# Asset Metadata (S3)

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, Forbidden

import json
import os, sys

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
    service_name="asset-metadata",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="asset-metadata", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="asset-metadata", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

BAD_METADATA = os.getenv('BAD_METADATA')  # "1" if metadata is in a bad state

with open("{}/asset-metadata.json".format(parent_path), "r") as f:
    metadata = json.load(f)

@app.route("/books/<book_id>/licenses/<license>", methods=['GET'])
def get_metadata(book_id, license):
    if BAD_METADATA == "1":
        # This is to simulate a NotFound coming from S3 (per the original example, 
        # when the system is in an inconsistent state from a failed upload of a book.)
        raise NotFound("book_id {} not found".format(book_id))
        
    if book_id not in metadata:
        raise NotFound("book_id {} not found".format(book_id))
    if not check_license(license):
        raise Forbidden("license invalid")

    response = {}
    response["metadata"] = metadata[book_id]
    return jsonify(response)

# Dummy check
def check_license(license):
    return license != "invalid_license"

if __name__ == "__main__":
    app.run(port=helper.get_port('asset-metadata'), host="0.0.0.0", debug=helper.get_debug())
