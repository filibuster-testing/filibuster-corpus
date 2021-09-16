
# mobile client

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, ServiceUnavailable, InternalServerError

import os
import sys
import requests

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("netflix")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="mobile-client",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="mobile-client", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="mobile-client", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)


@app.route("/netflix/homepage/users/<user_id>", methods=['GET'])
def get_netflix_homepage(user_id):
    try:
        api_gateway_response = requests.get("{}/homepage/users/{}".format(helper.get_service_url('api-gateway'), user_id), timeout=helper.get_timeout('api-gateway'))
        status_code = api_gateway_response.status_code

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The API Gateway is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The API Gateway timed out.")

    if status_code == 404:
        raise NotFound("user_id {} not found".format(user_id))
    if status_code == 503:
        raise ServiceUnavailable()
    if status_code == 500:
        raise ServiceUnavailable("netflix is unavailable.")

    res = api_gateway_response.json()
    return jsonify(res)


if __name__ == "__main__":
    app.run(port=helper.get_port('mobile-client'), host="0.0.0.0", debug=helper.get_debug())
