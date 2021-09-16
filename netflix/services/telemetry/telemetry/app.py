
# Telemetry

from flask import Flask, request, Response, jsonify
from werkzeug.exceptions import InternalServerError
from threading import Thread, Lock

import json
import os
import sys
import random

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
    service_name="telemetry",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="telemetry", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="telemetry", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration

@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_path)

file_path = "{}/logs.json".format(parent_path)

@app.route("/", methods=['POST'])
def record():
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                logs = json.load(f)
            if len(logs["logs"]) > 10:
                # truncate log
                logs["logs"] = []
            logs["logs"].append(request.json)
            with open(file_path, "w") as f:
                json.dump(logs, f)
        else:
            logs = {}
            logs["logs"] = []
            logs["logs"].append(request.json)
            with open(file_path, "w") as f:
                json.dump(logs, f)
    except:
        raise InternalServerError("Telemetry service error.")
    
    return Response(status=200)

if __name__ == "__main__":
    app.run(port=helper.get_port("telemetry"), host="0.0.0.0", debug=helper.get_debug())
