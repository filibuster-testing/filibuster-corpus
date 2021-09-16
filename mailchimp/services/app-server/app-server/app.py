
# App Server

from flask import Flask, jsonify
from werkzeug.exceptions import InternalServerError
import json, requests
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
    service_name="app-server",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="app-server", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="app-server", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def app_server_health_check():
    return jsonify({"status": "OK"})

@app.route("/urls/<url>", methods=['GET'])
def get_url(url):
    response = {}

    # Make call to requestmapper
    try:
        requestmapper_response = requests.get("http://{}:{}/urls/{}".format(helper.resolve_requests_host(
            'requestmapper'), helper.get_port('requestmapper'), url), timeout=helper.get_timeout('requestmapper'))
        status_code = requestmapper_response.status_code
        if status_code != 200:
            raise InternalServerError("Requestmapper error")
        response["result"] = requestmapper_response.json()["result"]
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise InternalServerError("Requestmapper error")

    # Make calls to DB
    primary_success = True
    try:
        db_primary_read_response = requests.get("http://{}:{}/read".format(helper.resolve_requests_host(
            'db-primary'), helper.get_port('db-primary')), timeout=helper.get_timeout('db-primary'))
        if db_primary_read_response.status_code != 200: 
            primary_success = False
        
        db_primary_write_response = requests.post("http://{}:{}/write/urls/{}".format(helper.resolve_requests_host(
            'db-primary'), helper.get_port('db-primary'), url), timeout=helper.get_timeout('db-primary'))
        if db_primary_write_response.status_code != 200:
            response["alert"] = "cannot write to DB"

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        primary_success = False

    if not primary_success:
        # Fallback to secondary DB
        try:
            db_secondary_read_response = requests.get("http://{}:{}/read".format(helper.resolve_requests_host(
                'db-secondary'), helper.get_port('db-secondary')), timeout=helper.get_timeout('db-secondary'))
            if db_secondary_read_response.status_code != 200:
                raise InternalServerError("DB error")

            db_secondary_write_response = requests.post("http://{}:{}/write/urls/{}".format(helper.resolve_requests_host(
                'db-secondary'), helper.get_port('db-secondary'), url), timeout=helper.get_timeout('db-secondary'))
            if db_secondary_write_response.status_code != 200:
                response["alert"] = "cannot write to DB"

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise InternalServerError("DB error")
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=helper.get_port('app-server'), host="0.0.0.0", debug=helper.get_debug())
