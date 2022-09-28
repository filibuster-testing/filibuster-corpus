from flask import Flask, jsonify
from werkzeug.exceptions import NotFound

import json
import os
import sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("cinema-11")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="movies",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="movies", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="movies", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration

with open("{}/cinema-11/services/movies/movies.json".format(examples_path), "r") as f:
    movies = json.load(f)

@app.route("/", methods=['GET'])
def hello():
    return jsonify({
        "uri": "/",
        "subresource_uris": {
            "movies": "/movies",
            "movie": "/movies/<id>"
        }
    })

@app.route("/health-check", methods=['GET'])
def movies_health_check():
    return jsonify({ "status": "OK" })

@app.route("/movies/<movieid>", methods=['GET'])
def movie_info(movieid):
    if movieid not in movies:
        raise NotFound

    result = movies[movieid]
    result["uri"] = "/movies/{}".format(movieid)

    return jsonify(result)

@app.route("/movies", methods=['GET'])
def movie_record():
    return jsonify(movies)

if __name__ == "__main__":
    app.run(port=helper.get_port('movies'), host="0.0.0.0", debug=helper.get_debug(), threaded=True)
