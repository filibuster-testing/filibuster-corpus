
# Audio Assets (S3)

from flask import Flask, send_from_directory, jsonify
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
    service_name="audio-assets",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="audio-assets", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="audio-assets", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})


parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

with open("{}/audio-assets.json".format(parent_path), "r") as f:
    assets = json.load(f)


@app.route("/books/<book_id>/licenses/<license>", methods=['GET'])
def get_audio(book_id, license):
    if book_id not in assets:
        raise NotFound("book_id {} not found".format(book_id))
    if not check_license(license):
        raise Forbidden("license invalid")
    
    try:
        audio_path = assets[book_id]["audio"]
        return send_from_directory(parent_path, audio_path, as_attachment=True)
    except:
        raise NotFound("audio file not found")

# Dummy check
def check_license(license):
    return license != "invalid_license"

if __name__ == "__main__":
    app.run(port=helper.get_port('audio-assets'), host="0.0.0.0", debug=helper.get_debug())
