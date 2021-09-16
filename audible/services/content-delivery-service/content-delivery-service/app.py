
# Content Delivery Service (EC2)

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, Forbidden, ServiceUnavailable, InternalServerError
import requests
import sys, os

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
    service_name="content-delivery-service",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="content-delivery-service", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="content-delivery-service", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})


@app.route("/users/<user_id>/books/<book_id>", methods=['GET'])
def retrieve_audio(user_id, book_id):
    response = {}

    # First, contact Audible Download Service (timeout = 5s)
    try:
        ads_response = requests.get("{}/users/{}/books/{}".format(helper.get_service_url('audible-download-service'), user_id, book_id), timeout=helper.get_timeout("audible-download-service"))
        if ads_response.status_code == 404:
            raise NotFound("user_id/book_id not found")
        if ads_response.status_code == 403:
            raise Forbidden("user_id {} does not own book_id {}".format(user_id, book_id))
        if ads_response.status_code == 503:
            raise ServiceUnavailable("Audible Download Service is unavailable")
        if ads_response.status_code != 200:
            raise InternalServerError()

        license = ads_response.json()["license"]

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Audible Download Service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Audible Download Service timed out.")
        
    # Authorized, try to get asset metadata (timeout = 1s)
    try:  
        metadata_response = requests.get("{}/books/{}/licenses/{}".format(helper.get_service_url("asset-metadata"), book_id, license), timeout=helper.get_timeout("asset-metadata"))
        if metadata_response.status_code == 404:
            raise NotFound("book_id {} not found".format(book_id))
        if metadata_response.status_code == 403:
            raise Forbidden("license incorrect")
        if metadata_response.status_code != 200:
            raise InternalServerError()

        response = metadata_response.json()

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Asset Metadata Service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Asset Metadata Service timed out.")

    # Finally, get audio assets (timeout = 2s)
    try:
        audio_response = requests.get("{}/books/{}/licenses/{}".format(helper.get_service_url("audio-assets"), book_id, license), timeout=helper.get_timeout("audio-assets"))
        if audio_response.status_code == 404:
            raise NotFound("book_id {} not found".format(book_id))
        if audio_response.status_code == 403:
            raise Forbidden("license incorrect")
        if audio_response.status_code != 200:
            raise InternalServerError()

    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Audio Assets Service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Audio Assets Service timed out.")
        
    return audio_response.content  # pretend that metadata is embedded


if __name__ == "__main__":
    app.run(port=helper.get_port('content-delivery-service'), host="0.0.0.0", debug=helper.get_debug())
