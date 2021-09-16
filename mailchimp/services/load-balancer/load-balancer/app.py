
# Load Balancer

from flask import Flask, jsonify
from werkzeug.exceptions import ServiceUnavailable, InternalServerError
import requests
import os, sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper
helper = helper.Helper("mailchimp")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="load-balancer",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="load-balancer", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="load-balancer", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def load_balancer_health_check():
    return jsonify({ "status": "OK" })


@app.route("/urls/<url>", methods=['GET'])
def convert(url):
    try:
        app_server_response = requests.get("http://{}:{}/urls/{}".format(
            helper.resolve_requests_host('app-server'), helper.get_port('app-server'), url), timeout=helper.get_timeout('load-balancer'))
        if app_server_response.status_code == 500:
            return jsonify({"result": url})
        return jsonify(app_server_response.json())
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise ServiceUnavailable("The App Server is unavailable.")


if __name__ == "__main__":
    app.run(port=helper.get_port('load-balancer'), host='0.0.0.0', debug=helper.get_debug())
