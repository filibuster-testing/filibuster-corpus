from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, ServiceUnavailable, TooManyRequests

import json
import requests
import os
import sys

app = Flask(__name__)

examples_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.append(examples_path)
import helper 
helper = helper.Helper("cinema-10")

## Start OpenTelemetry Configuration

from opentelemetry import trace
from opentelemetry.exporter import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(TracerProvider())

jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="users",
    agent_host_name=helper.jaeger_agent_host_name(),
    agent_port=helper.jaeger_agent_port()
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

sys.path.append(os.path.dirname(examples_path))
from filibuster.instrumentation.requests import RequestsInstrumentor as FilibusterRequestsInstrumentor
FilibusterRequestsInstrumentor().instrument(service_name="users", filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor
FilibusterFlaskInstrumentor().instrument_app(app, service_name="users", filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()

## End OpenTelemetry Configuration

docker = os.environ.get('RUNNING_IN_DOCKER', '')

with open("{}/cinema-10/services/users/users.json".format(examples_path), "r") as f:
    users = json.load(f)

@app.route("/", methods=['GET'])
def hello():
    return jsonify({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })

@app.route("/health-check", methods=['GET'])
def users_health_check():
    return jsonify({ "status": "OK" })

@app.route("/users", methods=['GET'])
def users_list():
    return jsonify(users)

@app.route("/users/<username>", methods=['GET'])
def user_record(username):
    if username not in users:
        raise NotFound

    return jsonify(users[username])

@app.route("/users/<username>/bookings", methods=['GET'])
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    if username not in users:
        raise NotFound("User '{}' not found.".format(username))

    fallback = False
    try:
        users_bookings = requests.get("http://{}:{}/bookings/{}".format(helper.resolve_requests_host('bookings'), helper.get_port('bookings'), username), timeout=helper.get_timeout('bookings'))
    except requests.exceptions.ConnectionError:
        fallback = True
    except requests.exceptions.Timeout:
        fallback = True


    if not fallback and users_bookings.status_code == 200:
        users_bookings = users_bookings.json()
    elif not fallback and users_bookings.status_code == 429:
        raise TooManyRequests
    else:
        users_bookings = {'20151201': ['267eedb8-0f5d-42d5-8f43-72426b9fb3e6']}
        

    # For each booking, get the rating and the movie title
    result = {}
    for date, movies in users_bookings.items():
        result[date] = []
        for movieid in movies:
            fallback = False
            try:
                movies_resp = requests.get("http://{}:{}/movies/{}".format(helper.resolve_requests_host('movies'), helper.get_port('movies'), movieid), timeout=helper.get_timeout('movies'))
            except requests.exceptions.ConnectionError:
                fallback = True
            except requests.exceptions.Timeout:
                fallback = True

            if not fallback and movies_resp.status_code == 200:
                movies_resp = movies_resp.json()
            else:
                movies_resp = {'title': 'Creed', 'rating': 8.8, 'director': 'Ryan Coogler',
                           'id': '267eedb8-0f5d-42d5-8f43-72426b9fb3e6', 'uri': '/movies/267eedb8-0f5d-42d5-8f43-72426b9fb3e6'}
            

            result[date].append({
                "title": movies_resp["title"],
                "rating": movies_resp["rating"],
                "uri": movies_resp["uri"]
            })
    return jsonify(result)


@app.route("/users/<username>/suggested", methods=['GET'])
def user_suggested(username):
    """
    Returns movie suggestions. The algorithm returns a list of 3 top ranked
    movies that the user has not yet booked.
    :param username:
    :return: Suggested movies
    """
    raise NotImplementedError()

if __name__ == "__main__":
    app.run(port=helper.get_port('users'), host="0.0.0.0", debug=helper.get_debug(), threaded=True)
