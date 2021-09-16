# API Gateway

from flask import Flask, jsonify
from werkzeug.exceptions import NotFound, ServiceUnavailable, InternalServerError
import requests
import time
import os
import sys

app = Flask(__name__)

examples_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
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

FilibusterRequestsInstrumentor().instrument(service_name="api-gateway",
                                            filibuster_url=helper.get_service_url('filibuster'))

from filibuster.instrumentation.flask import FlaskInstrumentor as FilibusterFlaskInstrumentor

FilibusterFlaskInstrumentor().instrument_app(app, service_name="api-gateway",
                                             filibuster_url=helper.get_service_url('filibuster'))

RequestsInstrumentor().instrument()


## End OpenTelemetry Configuration


@app.route("/health-check", methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})


# Load content from the Trending service (timeout = 1s)
def load_trending():
    try:
        trending_response = requests.get(helper.get_service_url('trending'), timeout=helper.get_timeout("trending"))
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("Fallback triggered and the Trending service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("Fallback triggered and the Trending service timed out.")

    if trending_response.status_code != 200:
        raise InternalServerError()

    return trending_response.json()["trending"]


# Make a call to the Telemetry service (timeout = 5s)
# Proceed even if there is an error
def call_telemetry():
    try:
        requests.post(helper.get_service_url("telemetry"), json={"time": time.time()}, timeout=helper.get_timeout("telemetry"))

    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass

    return None


# Get bookmarks (timeout = 1s)
def get_bookmarks(user_id):
    try:
        bookmarks_response = requests.get("{}/users/{}".format(helper.get_service_url("bookmarks"), user_id),
                                          timeout=helper.get_timeout("bookmarks"))
        if bookmarks_response.status_code != 200:
            return None
        else:
            return bookmarks_response.json()["bookmarks"]
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass

    return None


# Get User Profile (timeout = 1s)
def get_user_profile(user_id):
    # Conditionally use a timeout that's too short.
    if os.environ.get('NETFLIX_FAULTS', ''):
        timeout = 1
    else:
        timeout = helper.get_timeout("user-profile")

    try:
        user_profile_response = requests.get("{}/users/{}".format(helper.get_service_url("user-profile"), user_id),
                                             timeout=timeout)
        status_code = user_profile_response.status_code
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The My List service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The My List service timed out.")

    if status_code == 404:
        raise NotFound("user_id {} not found".format(user_id))
    if status_code != 200:
        raise InternalServerError()

    res = user_profile_response.json()

    return res


# Get My List (timeout = 1s)
def get_my_list(user_id):
    try:
        my_list_response = requests.get("{}/users/{}".format(helper.get_service_url("my-list"), user_id),
                                        timeout=helper.get_timeout("my-list"))
        status_code = my_list_response.status_code
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        if os.environ.get('NETFLIX_FAULTS', ''):
            # fallback, try same server again.
            try:
                my_list_response = requests.get("{}/users/{}".format(helper.get_service_url("my-list"), user_id),
                                                timeout=helper.get_timeout("my-list"))
                status_code = my_list_response.status_code
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                raise ServiceUnavailable("The My List service is unavailable.")
        else:
            raise ServiceUnavailable("The My List service is unavailable.")

    if status_code == 404:
        raise NotFound("user_id {} not found".format(user_id))
    if status_code != 200:
        raise InternalServerError()

    res = my_list_response.json()["my-list"]

    return res


# Get User Recommendations (timeout = 1s)
def get_user_rec(user_id):
    try:
        user_rec_response = requests.get("{}/users/{}".format(helper.get_service_url("user-recommendations"), user_id),
                                         timeout=helper.get_timeout("user-recommendations"))
        if user_rec_response.status_code != 200:
            return None
        else:
            return user_rec_response.json()["recommendations"]
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass


# Get Global Recommendations (timeout = 1s)
def get_global_rec():
    try:
        global_rec_response = requests.get(helper.get_service_url("global-recommendations"),
                                           timeout=helper.get_timeout("global-recommendations"))
        if global_rec_response.status_code != 200:
            return None
        else:
            return global_rec_response.json()["recommendations"]
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass


# Get Ratings (timeout = 1s)
def get_ratings(user_id):
    try:
        ratings_response = requests.get("{}/users/{}".format(helper.get_service_url("ratings"), user_id),
                                        timeout=helper.get_timeout("ratings"))
        status_code = ratings_response.status_code
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Ratings service is unavailable.")
    except requests.exceptions.Timeout:
        raise ServiceUnavailable("The Ratings service timed out.")

    if status_code == 404:
        raise NotFound("user_id {} not found".format(user_id))
    if status_code != 200:
        raise InternalServerError()

    res = ratings_response.json()["ratings"]

    return res


@app.route("/homepage/users/<user_id>", methods=['GET'])
def get_homepage(user_id):
    response = {}

    # Get User Profile
    response["user-profile"] = get_user_profile(user_id)
    # Get Bookmarks
    bookmarks = get_bookmarks(user_id)

    if bookmarks is not None:
        response["bookmarks"] = bookmarks
    else: 
        # Fallback behavior:
        # Make a call to the Telemetry service and then load content from the Trending service
        print("Bookmarks fail: fallback to Telemetry and Trending", flush=True)
        call_telemetry()
        response["trending"] = load_trending()

    # Get My List
    response["my-list"] = get_my_list(user_id)

    # Get User Recommendations
    user_rec = get_user_rec(user_id)
    if user_rec is not None:
        response["recommendations"] = user_rec
    else:
        # Fallback behavior
        # Load content from the Global Recommendations
        print("User Recommendations fail: fallback to Global Recommendations", flush=True)
        global_rec = get_global_rec()
        if global_rec is not None:
            response["recommendations"] = global_rec
        else:
            # Fallback behavior:
            # Load content from the Trending service
            print("Global Recommendations fail: fallback to Trending", flush=True)
            if "trending" not in response:
                response["trending"] = load_trending()

    # Get Ratings (timeout = 1s)
    response["ratings"] = get_ratings(user_id)

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=helper.get_port('api-gateway'), host="0.0.0.0", debug=helper.get_debug())
