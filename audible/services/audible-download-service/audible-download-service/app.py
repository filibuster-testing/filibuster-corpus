
# Audible Download Service (EC2)

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, Forbidden, ServiceUnavailable, InternalServerError
import requests
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
    service_name="audible-download-service",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="audible-download-service", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="audible-download-service", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})


parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

@app.route("/users/<user_id>/books/<book_id>", methods=['GET'])
def auth_and_log(user_id, book_id):
    response = {}
    # First, verify ownership (timeout = 1s)
    try:
        ownership_response = requests.get("{}/users/{}/books/{}".format(helper.get_service_url("ownership"), user_id, book_id), timeout=helper.get_timeout("ownership"))
        if ownership_response.status_code == 404:
            raise NotFound("user_id {} not found".format(user_id))
        if ownership_response.status_code == 403:
            raise Forbidden("user_id {} does not own book_id {}".format(user_id, book_id))
        if ownership_response.status_code != 200:
            raise InternalServerError()

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Ownership Service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Ownership Service timed out.")
        
    # Next, get a license (timeout = 1s)
    try:
        activation_response = requests.get("{}/books/{}".format(helper.get_service_url("activation"), book_id), timeout=helper.get_timeout("activation"))
        if activation_response.status_code == 404:
            raise NotFound("book_id {} not found".format(book_id))
        if activation_response.status_code != 200:
            raise InternalServerError()

        response = activation_response.json()

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Audible Download Service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Audible Download Service timed out.")

    # Finally, record stats (timeout = 1s)
    # ignore failures because this is a non-critical service
    try:
        stats_response = requests.post("{}/users/{}/books/{}".format(helper.get_service_url("stats"), user_id, book_id), timeout=helper.get_timeout("stats"))
        if stats_response.status_code != 201:
            print("Stats service errored")
    except Exception as e:
        print("Failed to connect to Stats service: {}".format(str(e)))

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=helper.get_port('audible-download-service'), host="0.0.0.0", debug=helper.get_debug())
