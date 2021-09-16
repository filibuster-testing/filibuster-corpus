from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, ServiceUnavailable

import json
import os
import sys
import requests

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("cinema-8")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="api-server",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="api-server", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="api-server", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def api_server_health_check():
    return jsonify({ "status": "OK" })

@app.route("/users/<username>/bookings", methods=['GET'])
def api_server_record(username):
    RETRIES = 2

    for i in range(0, RETRIES):
        try:
            users_bookings = requests.get("http://{}:{}/users/{}/bookings".format(helper.resolve_requests_host(
                'monolith'), helper.get_port('monolith'), username), timeout=helper.get_timeout('monolith'))
            if users_bookings.status_code == 200:
                break

        except requests.exceptions.ConnectionError:
            if i == RETRIES - 1:
                raise ServiceUnavailable("The monolith is unavailable.")
        except requests.exceptions.Timeout:
            if i == RETRIES - 1:
                raise ServiceUnavailable("The monolith timed out.")

    if users_bookings.status_code == 404:
        raise NotFound("No bookings were found for {}".format(username))

    if users_bookings.status_code != 200:
        raise ServiceUnavailable("The Bookings service is malfunctioning.")

    users_bookings = users_bookings.json()

    return jsonify(users_bookings)
    

if __name__ == "__main__":
    app.run(port=helper.get_port('api-server'), host="0.0.0.0", debug=helper.get_debug())
