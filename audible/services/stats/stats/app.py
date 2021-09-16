
# Stats service (Amazon RDS)

from flask import Flask, Response, jsonify
from werkzeug.exceptions import InternalServerError
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
    service_name="stats",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="stats", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="stats", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration

@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

file_path = "{}/stats.json".format(parent_path)

@app.route("/users/<user_id>/books/<book_id>", methods=['POST'])
def record(user_id, book_id):
    # Record user activity
    try:
        # Append to existing log and truncate if the log is too long.
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                stats = json.load(f)
            if len(stats["logs"]) > 10:
                # truncate log
                stats["logs"] = []
            stats["logs"].append({'user_id': user_id, 'book_id': book_id})
            with open(file_path, "w") as f:
                json.dump(stats, f)
        # File doesn't exist, therefore we have to create it.
        else:
            stats = {}
            stats["logs"] = []
            stats["logs"].append({'user_id': user_id, 'book_id': book_id})
            with open(file_path, "w") as f:
                json.dump(stats, f)
    except:
        raise InternalServerError("Stats service error.")

    return Response(status=201)

if __name__ == "__main__":
    app.run(port=helper.get_port('stats'), host="0.0.0.0", debug=helper.get_debug())