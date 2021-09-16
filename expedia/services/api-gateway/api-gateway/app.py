
# API Gateway

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, ServiceUnavailable, InternalServerError
import requests
import os, sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("expedia")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="api-gateway",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="api-gateway", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="api-gateway", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

@app.route("/review/hotels/<hotel_id>", methods=['GET'])
def get_homepage(hotel_id):

    # Get ML sorted reviews
    result = None
    success = True
    try:
        reviews_response = requests.get("http://{}:{}/hotels/{}".format(helper.resolve_requests_host(
            'review-ml'), helper.get_port('review-ml'), hotel_id), timeout=helper.get_timeout('review-ml'))
        status_code = reviews_response.status_code
        if status_code == 404:
            raise NotFound("hotel_id {} not found".format(hotel_id))
        if status_code != 200:
            success = False
        else:
            result = reviews_response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        success = False

    if success:
        return jsonify(result)
            
    # Fallback to time sorted reviews
    try:
        reviews_response = requests.get("http://{}:{}/hotels/{}".format(helper.resolve_requests_host(
            'review-time'), helper.get_port('review-time'), hotel_id), timeout=helper.get_timeout('review-time'))
        status_code = reviews_response.status_code
        if status_code == 404:
            raise NotFound("hotel_id {} not found".format(hotel_id))
        if status_code != 200:
            raise ServiceUnavailable("Reviews are unavailable.")
        result = reviews_response.json()
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("Fallback review service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("Fallback review service timed out.")
            
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=helper.get_port('api-gateway'), host="0.0.0.0", debug=helper.get_debug())
