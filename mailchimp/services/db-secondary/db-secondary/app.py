
# Secondary Database

from flask import Flask, Response, jsonify
from werkzeug.exceptions import Forbidden
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
    service_name="db-secondary",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="db-secondary", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="db-secondary", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def db_secondary_health_check():
    return jsonify({ "status": "OK" })


@app.route("/read", methods=['GET'])
def read():
    return jsonify({"data": "dummy"})


READ_ONLY = os.getenv('DB_READ_ONLY') # "1" if DB is read only


@app.route("/write/urls/<url>", methods=['POST'])
def write(url):
    # In PHP (which, Mailchimp uses) the database error renders directly into the output.
    # So to simulate that we put something manually into the JSON when an error occurs.
    if READ_ONLY == "1":
        raise Forbidden("Database is read-only")

    return Response(status=200)


if __name__ == "__main__":
    app.run(port=helper.get_port('db-secondary'), host="0.0.0.0", debug=helper.get_debug())
