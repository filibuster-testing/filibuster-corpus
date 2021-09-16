
# Audible App

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, Forbidden, ServiceUnavailable, InternalServerError
import requests
import sys
import os

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
    service_name="audible-app",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="audible-app", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="audible-app", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)


@app.route("/users/<user_id>/books/<book_id>", methods=['GET'])
def retrieve_audio(user_id, book_id):
    RETRY_LOOP_CDE = 1
    RETRY_LOOP_CDS = 1

    # First, contact Content Delivery Engine (timeout = 1s)
    for i in range(0, RETRY_LOOP_CDE):
        try:
            cde_response = requests.get("{}/users/{}/books/{}".format(helper.get_service_url(
                "content-delivery-engine"), user_id, book_id), timeout=helper.get_timeout("content-delivery-engine"))
            if cde_response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if i == RETRY_LOOP_CDE - 1:
                raise ServiceUnavailable(
                    "The Content Delivery Engine is unavailable.")
        except requests.exceptions.Timeout:
            if i == RETRY_LOOP_CDE - 1:
                raise ServiceUnavailable(
                    "The Content Delivery Engine timed out.")

    if cde_response.status_code == 404:
        raise NotFound("user_id/book_id not found")
    if cde_response.status_code != 200:
        raise ServiceUnavailable("The Content Delivery Engine had an error.")

    # Then, contact Content Delivery Service (timeout = 10s)
    for i in range(0, RETRY_LOOP_CDS):
        try:
            cds_response = requests.get(cde_response.json(
            )["url"], timeout=helper.get_timeout("content-delivery-service"))
            if cds_response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            if i == RETRY_LOOP_CDS - 1:
                raise ServiceUnavailable(
                    "The Content Delivery Service is unavailable.")
        except requests.exceptions.Timeout:
            if i == RETRY_LOOP_CDS - 1:
                raise ServiceUnavailable(
                    "The Content Delivery Service timed out.")

    if cds_response.status_code == 404:
        raise NotFound("user_id/book_id not found")
    if cds_response.status_code == 403:
        raise Forbidden("user_id does not own book_id or license mismatch")
    if cds_response.status_code == 503:
        raise ServiceUnavailable(
            "The Content Delivery Service is unavailable.")
    if cds_response.status_code != 200:
        raise ServiceUnavailable("The Content Delivery Service had an error.")

    return cds_response.content


if __name__ == "__main__":
    app.run(port=helper.get_port('audible-app'), host="0.0.0.0", debug=helper.get_debug())
